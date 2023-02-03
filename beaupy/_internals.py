from ast import literal_eval
from contextlib import contextmanager
from typing import Any, Callable, Iterator, List, Type, Union

import emoji
from rich.console import Console, ConsoleRenderable
from rich.live import Live
from yakh.key import Key

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


def _render_option_select_multiple(
    option: str, ticked: bool, tick_character: str, tick_style: str, selected: bool, cursor_style: str
) -> str:
    prefix = '\[{}]'.format(' ' * len(_replace_emojis(tick_character)))  # noqa: W605
    if ticked:
        prefix = f'\[[{tick_style}]{tick_character}[/{tick_style}]]'  # noqa: W605
    if selected:
        option = f'[{cursor_style}]{option}[/{cursor_style}]'
    return f'{prefix} {option}'


def _update_rendered(live: Live, renderable: Union[ConsoleRenderable, str]) -> None:
    live.update(renderable=renderable)
    live.refresh()


def _render_prompt(secure: bool, typed_values: List[str], prompt: str, cursor_position: int, error: str) -> str:
    render_value = (len(typed_values) * '*' if secure else ''.join(typed_values)) + ' '
    render_value = (
        render_value[:cursor_position]
        + '[black on white]'  # noqa: W503
        + render_value[cursor_position]  # noqa: W503
        + '[/black on white]'  # noqa: W503
        + render_value[(cursor_position + 1) :]  # noqa: W503,E203
    )
    render_value = f'{prompt}\n> {render_value}\n\n(Confirm with [bold]enter[/bold])'
    if error:
        render_value = f'{render_value}\n[red]Error:[/red] {error}'
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
