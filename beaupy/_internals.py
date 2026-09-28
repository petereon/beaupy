import copy
import math
import re
from ast import literal_eval
from contextlib import contextmanager
from types import ModuleType
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Type, Union

import emoji
from questo import prompt as qprompt
from questo import select as qselect
from rich.console import Console, ConsoleRenderable
from rich.live import Live
from rich.markup import escape
from rich.style import Style
from rich.text import Text
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


_REMOVED_GLOBALS = {
    'console': (
        '`beaupy.console` was removed in beaupy 4.0.0 because it was shared by the whole process. '
        'Pass your own console instead: `select(options, config=Config(console=my_console))`.'
    ),
    'DefaultKeys': (
        '`beaupy.DefaultKeys` was removed in beaupy 4.0.0 because changing it affected the whole process. '
        'Pass keybindings instead: `select(options, config=Config(keys=KeyBindings(up=[...])))`.'
    ),
}


class RemovedInV4Error(ImportError):
    """Raised when code uses a global that was removed in beaupy 4.0.0.

    Not an AttributeError on purpose: `from beaupy import console` would swallow it and hide the migration message.
    """


class _RemovedGlobalsModule(ModuleType):
    """Turns access to globals removed in 4.0.0 into an error that explains the migration."""

    def __getattr__(self, name: str) -> Any:
        if name in _REMOVED_GLOBALS:
            raise RemovedInV4Error(_REMOVED_GLOBALS[name])
        raise AttributeError(f'module {self.__name__!r} has no attribute {name!r}')

    def __setattr__(self, name: str, value: Any) -> None:
        if name in _REMOVED_GLOBALS:
            raise RemovedInV4Error(_REMOVED_GLOBALS[name])
        super().__setattr__(name, value)


class _InstanceOnly(type):
    """Metaclass that forbids assigning attributes on the class itself once `_locked` is set.

    In 3.x, `Config.raise_on_escape = True` changed behaviour globally. In 4.0.0 settings live on instances.
    """

    _locked = False

    def __setattr__(cls, name: str, value: Any) -> None:
        if cls._locked:
            example = f'{cls.__name__}({name}=...)'
            if cls.__name__ != 'Config':
                example = f'Config(keys={example})'
            raise AttributeError(
                f'Setting `{cls.__name__}.{name}` on the class was removed in beaupy 4.0.0 because it changed behaviour globally. '
                f'Pass an instance to each call instead: `select(options, config={example})`.'
            )
        super().__setattr__(name, value)


SectionedPosition = Tuple[str, int]


def _flatten_options(options: Union[List[Any], Dict[str, List[Any]]]) -> Tuple[List[Any], List[Optional[str]], List[Any]]:
    """Returns flat options, the section of each option (None if not sectioned) and the user-facing position of each option.

    For a list, position is the list index. For a dict, it's `(section_name, index_within_section)`.
    """
    if isinstance(options, dict):
        flat = [(section, i, option) for section, section_options in options.items() for i, option in enumerate(section_options)]
        return [option for _, _, option in flat], [section for section, _, _ in flat], [(section, i) for section, i, _ in flat]
    return list(options), [None] * len(options), list(range(len(options)))


def _option_labels(options: List[Any], preprocessor: Callable[[Any], str]) -> List[str]:
    """Lowercased plain text of each option as displayed, used for filtering."""
    return [Text.from_markup(preprocessor(option)).plain.lower() for option in options]


def _visible_indexes(state: qselect.SelectState, labels: List[str]) -> List[int]:
    if not state.filter:
        return list(range(len(state.options)))
    query = state.filter.lower()
    return [i for i, label in enumerate(labels) if query in label]


def _to_flat_index(positions: List[Any], index: Union[int, SectionedPosition, None]) -> int:
    """Translates a user-facing index (int for list options, `(section, index)` for dict options) to a flat one."""
    if index is None:
        return 0
    sectioned = isinstance(positions[0], tuple)
    if not sectioned:
        if isinstance(index, tuple):
            raise TypeError(f'Index {index!r} is a `(section_name, index_in_section)` tuple, but `options` is a list. Use an int.')
        return index
    if not isinstance(index, tuple):
        raise TypeError(
            f'Index {index!r} must be a `(section_name, index_in_section)` tuple because `options` is a dict of sections, '
            f'e.g. {positions[0]!r}.'
        )
    if index not in positions:
        raise ValueError(f'`options` has no option at {index!r}.')
    return positions.index(index)


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
            # ignores invalid colors in square brackets, since these aren't styles
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


def _render_prompt(secure: bool, instructions: Optional[str], state: qprompt.PromptState) -> str:
    typed_values = [*(state.value or '')]
    input_value = len(typed_values) * '*' if secure else ''.join(typed_values)

    # Escape backslashes to prevent them from being interpreted as escape characters
    cursor_position = state.cursor_position + input_value.count('\\')
    input_value = input_value.replace('\\', '\\\\')

    render_value = (  # noqa: ECE001
        (input_value + ' ')[:cursor_position]
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

    render_value = f'{state.title}\n> {render_value}' + (f'\n\n{instructions}' if instructions else '')
    if state.error:
        render_value = f'{render_value}\n[red]Error:[/red] {state.error}'

    return render_value


def _render_options(
    state: qselect.SelectState,
    sections: List[Optional[str]],
    labels: List[str],
    render_option: Callable[[int, Any], str],
    title: str,
    instructions: Optional[str],
) -> str:
    visible = _visible_indexes(state, labels)
    position = visible.index(state.index) if state.index in visible else 0
    page: int = position // state.page_size + 1
    total_pages = max(1, math.ceil(len(visible) / state.page_size))

    shown = visible[(page - 1) * state.page_size : page * state.page_size] if state.pagination else visible  # noqa: E203

    header = title
    if state.filter:
        header = f'{header} [grey58]{escape(state.filter)}[/grey58]'.strip()
    lines = [header] if header else []
    for k, i in enumerate(shown):
        # Header on section change, and repeated at the top of a page so the reader keeps context
        if sections[i] is not None and (k == 0 or sections[i] != sections[shown[k - 1]]):
            lines.append(f'[bold]{sections[i]}[/bold]')
        lines.append(render_option(i, state.options[i]))

    return (  # noqa: ECE001
        '\n'.join(lines)
        + (f'[grey58]\n\nPage {page}/{total_pages}[/grey58]' if state.pagination and total_pages > 1 else '')  # noqa: W503
        + (f'\n\n{instructions}' if instructions else '')  # noqa: W503
    )


def _render_select(
    preprocessor: Callable[[Any], str],
    cursor_style: str,
    cursor: str,
    title: str,
    instructions: Optional[str],
    sections: List[Optional[str]],
    labels: List[str],
    state: qselect.SelectState,
) -> str:
    return _render_options(
        state,
        sections,
        labels,
        lambda i, option: _render_option_select(
            i=i, cursor_index=state.index, option=preprocessor(option), cursor_style=cursor_style, cursor=cursor
        ),
        title,
        instructions,
    )


def _render_select_multiple(
    preprocessor: Callable[[Any], str],
    tick_character: str,
    tick_style: str,
    cursor_style: str,
    title: str,
    instructions: Optional[str],
    sections: List[Optional[str]],
    labels: List[str],
    state: qselect.SelectState,
) -> str:
    rendered = _render_options(
        state,
        sections,
        labels,
        lambda i, option: _render_option_select_multiple(
            option=preprocessor(option),
            ticked=i in state.selected_indexes,
            tick_character=tick_character,
            tick_style=tick_style,
            selected=i == state.index,
            cursor_style=cursor_style,
        ),
        title,
        instructions,
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
