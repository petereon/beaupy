import copy
import re
from ast import literal_eval
from contextlib import contextmanager
from typing import Any, Callable, Iterator, List, Tuple, Type, Union

import emoji
from questo import prompt as qprompt
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


def _format_option_select(i: int, cursor_index: int, option: str, cursor_style: str, cursor: str) -> str:
    return '{}{}'.format(
        f'[{cursor_style}]{cursor}[/{cursor_style}] ' if i == cursor_index else ' ' * (len(_replace_emojis(cursor)) + 1), option
    )


def _wrap_style(string_w_styles: str, global_style_str: str) -> str:
    RE_STYLE_PATTERN = r'\[(.*?)\]'

    global_style = Style.parse(global_style_str)
    style_strings = list(set([i.replace('/', '') for i in re.findall(RE_STYLE_PATTERN, string_w_styles)]))
    for style_string in style_strings:
        style = Style.combine([Style.parse(style_string), global_style])
        string_w_styles = string_w_styles.replace(f'{style_string}', f'{style}')

    return f'[{global_style_str}]{string_w_styles}[/{global_style_str}]'


def _render_option_select_multiple(
    option: str, ticked: bool, tick_character: str, tick_style: str, selected: bool, cursor_style: str
) -> str:
    prefix = '\[{}]'.format(' ' * len(_replace_emojis(tick_character)))  # noqa: W605
    if ticked:
        prefix = f'\[[{tick_style}]{tick_character}[/{tick_style}]]'  # noqa: W605
    if selected:
        option = _wrap_style(option, cursor_style)
    return f'{prefix} {option}'


def _update_rendered(live: Live, renderable: Union[ConsoleRenderable, str]) -> None:
    live.update(renderable=renderable)
    live.refresh()


def _render_prompt(secure: bool, state: qprompt.PromptState) -> str:
    typed_values = [*(state.value or '')]
    input_value = len(typed_values) * '*' if secure else ''.join(typed_values)
    render_value = (  # noqa: ECE001
        (input_value + ' ')[: state.cursor_position]
        + '[black on white]'  # noqa: W503
        + (input_value + ' ')[state.cursor_position]  # noqa: W503
        + '[/black on white]'  # noqa: W503
        + (input_value + ' ')[(state.cursor_position + 1) :]  # noqa: W503,E203
    )

    if state.completion.options and not secure:
        rendered_completion_options = ' '.join(state.completion.options).replace(
            input_value, f'[black on white]{input_value}[/black on white]'
        )
        render_value = f'{render_value}\n{rendered_completion_options}'

    render_value = f'{state.title}\n> {render_value}\n\n(Confirm with [bold]enter[/bold])'
    if state.error:
        render_value = f'{render_value}\n[red]Error:[/red] {state.error}'

    return render_value


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
    elif keypress == Keys.UP_ARROW:
        pass
    elif keypress == Keys.DOWN_ARROW:
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
    cursor_positon = len(value)
    return index, cursor_positon, value
