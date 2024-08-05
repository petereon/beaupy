import copy
import math
import re
from ast import literal_eval
from contextlib import contextmanager
from typing import Any, Callable, Iterator, List, Tuple, Type, Union

import emoji
from questo import prompt as qprompt
from questo import select as qselect
from rich.console import Console, ConsoleRenderable
from rich.live import Live
from rich.style import Style
from yakh.key import Key, Keys

TargetType = Any


class ValidationError(Exception):
    pass


class ConversionError(Exception):
    pass


class Abort(Exception):
    key: Key

    def __init__(self, key: Key) -> None:
        super().__init__(f'Aborted by user with key {key.key if key.is_printable else key.key_codes}')
        self.key = key


def _replace_emojis(text: str) -> str:
    return str(emoji.replace_emoji(text, '  '))


def _render_option_select(i: int, cursor_index: int, option: str, cursor_style: str, cursor: str) -> str:
    return '{}{}'.format(
        f'[{cursor_style}]{cursor}[/{cursor_style}] ' if i == cursor_index else ' ' * (len(_replace_emojis(cursor)) + 1), option
    )


def _wrap_style(string_w_styles: str, global_style_str: str) -> str:
    RE_STYLE_PATTERN = r'\[(/?[^]]+)\]'

    global_style = Style.parse(global_style_str)
    style_strings = list(set(re.findall(RE_STYLE_PATTERN, string_w_styles)))
    for style_string in style_strings:
        try:
            style = Style.combine([Style.parse(style_string), global_style])
            string_w_styles = string_w_styles.replace(f'[{style_string}]', f'[{style}]')
            string_w_styles = string_w_styles.replace(f'[/{style_string}]', f'[/{style}]')
        except Exception:
            # In the case where there are non style defining square brakets in the string,
            # ignores invalid colors in square brakets, since these aren't styles
            continue

    return f'[{global_style_str}]{string_w_styles}[/{global_style_str}]'


def _render_option_select_multiple(
    option: str, ticked: bool, tick_character: str, tick_style: str, selected: bool, cursor_style: str
) -> str:
    prefix = r'\[{}]'.format(' ' * len(_replace_emojis(tick_character)))
    if ticked:
        prefix = rf'\[[{tick_style}]{tick_character}[/{tick_style}]]'
    if selected:
        option = _wrap_style(option, cursor_style)
    return f'{prefix} {option}'


def _update_rendered(live: Live, renderable: Union[ConsoleRenderable, str]) -> None:
    live.update(renderable=renderable)
    live.refresh()


def _render_prompt(secure: bool, state: qprompt.PromptState) -> str:
    typed_values = [*(state.value or '')]
    input_value = len(typed_values) * '*' if secure else ''.join(typed_values)

    # Escape backslashes to prevent them from being interpreted as escape characters
    cursor_position = state.cursor_position + input_value.count('\\')
    input_value = input_value.replace('\\', '\\\\')

    render_value = (  # noqa: ECE001
        (input_value + ' ')[: cursor_position]
        + '[black on white]'  # noqa: W503
        + (input_value + ' ')[cursor_position]  # noqa: W503
        + '[/black on white]'  # noqa: W503
        + (input_value + ' ')[(cursor_position + 1) :]  # noqa: W503,E203
    )

    if state.completion.options and not secure:
        rendered_completion_options = ' '.join(state.completion.options).replace(
            input_value, f'[black on white]{input_value}[/black on white]'
        )
        render_value = f'{render_value}\n{rendered_completion_options}'

    render_value = f'{state.title}\n> {render_value}\n\n([bold]enter[/bold] to confirm)'
    if state.error:
        render_value = f'{render_value}\n[red]Error:[/red] {state.error}'

    return render_value


def _render_select(preprocessor: Callable[[Any], str], cursor_style: str, cursor: str, state: qselect.SelectState) -> str:
    page: int = state.index // state.page_size + 1
    total_pages = math.ceil(len(state.options) / state.page_size)

    show_from = (page - 1) * state.page_size
    show_to = min(show_from + state.page_size, len(state.options))

    return (  # noqa: ECE001
        '\n'.join(
            [
                _render_option_select(
                    i=i,
                    cursor_index=state.index % state.page_size if state.pagination else state.index,
                    option=preprocessor(option),
                    cursor_style=cursor_style,
                    cursor=cursor,
                )
                for i, option in enumerate(state.options[show_from:show_to] if state.pagination else state.options)
            ]
        )
        + (f'[grey58]\n\nPage {page}/{total_pages}[/grey58]' if state.pagination and total_pages > 1 else '')  # noqa: W503
        + '\n\n([bold]enter[/bold] to confirm)'  # noqa: W503
    )


def _render_select_multiple(
    preprocessor: Callable[[Any], str], tick_character: str, tick_style: str, cursor_style: str, state: qselect.SelectState
) -> str:
    page: int = state.index // state.page_size + 1
    total_pages = math.ceil(len(state.options) / state.page_size)

    show_from = (page - 1) * state.page_size
    show_to = min(show_from + state.page_size, len(state.options))

    rendered = (  # noqa: ECE001
        '\n'.join(
            [
                _render_option_select_multiple(
                    option=preprocessor(option),
                    ticked=(i + show_from in state.selected_indexes) if state.pagination else (i in state.selected_indexes),
                    tick_character=tick_character,
                    tick_style=tick_style,
                    selected=i == (state.index % state.page_size if state.pagination else state.index),
                    cursor_style=cursor_style,
                )
                for i, option in enumerate(state.options[show_from:show_to] if state.pagination else state.options)
            ]
        )
        + (f'[grey58]\n\nPage {page}/{total_pages}[/grey58]' if state.pagination and total_pages > 1 else '')  # noqa: W503
        + '\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)'  # noqa: W503
    )
    if state.error:
        rendered = f'{rendered}\n[red]Error:[/red] {state.error}'
    return rendered


@contextmanager
def _cursor_hidden(console: Console) -> Iterator:
    console.show_cursor(False)
    yield
    console.show_cursor(True)


def _validate_prompt_value(
    value: List[str],
    target_type: Type[TargetType],
    validator: Callable[[TargetType], bool],
    secure: bool,
) -> TargetType:
    str_value = ''.join(value)
    try:
        if target_type is bool:
            result: bool = literal_eval(str_value)
            if not isinstance(result, bool):
                raise ValueError('Bool conversion failed')
        else:
            result: target_type = target_type(str_value)  # type: ignore
        if validator(result):
            return result
        else:
            error = f"Input {'<secure_input>' if secure else '`'+str_value+'`'} is invalid"
            raise ValidationError(error)
    except ValueError:
        error = f"Input {'<secure_input>' if secure else '`'+str_value+'`'} cannot be converted to type `{target_type}`"
        raise ConversionError(error)


def _paginate_forward(page_num: int, total_pages: int) -> int:
    if page_num < total_pages:
        page_num += 1
    else:
        page_num = 1
    return page_num


def _paginate_back(page: int, total_pages: int) -> int:
    if page > 1:
        page -= 1
    else:
        page = total_pages
    return page


def _prompt_key_handler(prompt_state: qprompt.PromptState, keypress: Key) -> qprompt.PromptState:
    s = copy.deepcopy(prompt_state)

    if keypress == Keys.TAB:
        if s.completion.in_completion_ctx and s.completion.options:
            s.completion.index, s.cursor_position, s.value = _completions_options_step(s)
        else:
            s.completion.in_completion_ctx = True
            s.completion.index = 0
            s.value = s.completion.options[0] if s.completion.options else s.value
            s.cursor_position = len(s.value)
    else:
        s.completion.in_completion_ctx = False
        s.completion.options = []
        s.completion.index = None

    if keypress == Keys.CTRL_C:
        s.value = None
        s.abort = True
    elif keypress == Keys.ENTER:
        s.exit = True
    elif keypress == Keys.LEFT_ARROW:
        if s.cursor_position > 0:
            s.cursor_position -= 1
    elif keypress == Keys.RIGHT_ARROW:
        if s.cursor_position < len(s.value):
            s.cursor_position += 1
    elif keypress == Keys.HOME:
        s.cursor_position = 0
    elif keypress == Keys.END:
        s.cursor_position = len(s.value)
    elif keypress == Keys.DELETE:
        if s.cursor_position < len(s.value):
            value_chars = [*s.value]
            del value_chars[s.cursor_position]
            s.value = ''.join(value_chars)
    elif keypress == Keys.BACKSPACE:
        if s.cursor_position > 0:
            s.cursor_position -= 1
            value_chars = [*s.value]
            del value_chars[s.cursor_position]
            s.value = ''.join(value_chars)
    elif keypress == Keys.ESC:
        s.exit = True
    elif keypress == Keys.UP_ARROW or keypress == Keys.DOWN_ARROW:
        pass
    elif keypress:
        if not (keypress == Keys.TAB and s.completion.in_completion_ctx):
            value_chars = [*s.value]
            value_chars.insert(s.cursor_position, str(keypress))
            s.cursor_position += 1
            s.value = ''.join(value_chars)

    return s


def _completions_options_step(state: qprompt.PromptState) -> Tuple[int, int, str]:
    index = (state.completion.index + 1) % len(state.completion.options)
    value = state.completion.options[index]
    cursor_position = len(value)
    return index, cursor_position, value
