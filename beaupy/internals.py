from contextlib import contextmanager
from typing import Iterator, List, Union

import emoji
from rich.console import Console, ConsoleRenderable
from rich.live import Live


class ValidationError(Exception):
    pass


class ConversionError(Exception):
    pass


def __replace_emojis(text: str) -> str:
    return str(emoji.replace_emoji(text, '  '))


def format_option_select(i: int, cursor_index: int, option: str, cursor_style: str, cursor: str) -> str:
    return '{}{}'.format(
        f'[{cursor_style}]{cursor}[/{cursor_style}] ' if i == cursor_index else ' ' * (len(__replace_emojis(cursor)) + 1), option
    )


def format_option_select_multiple(
    option: str, ticked: bool, tick_character: str, tick_style: str, selected: bool, cursor_style: str
) -> str:
    prefix = '\[{}]'.format(' ' * len(__replace_emojis(tick_character)))  # noqa: W605
    if ticked:
        prefix = f'\[[{tick_style}]{tick_character}[/{tick_style}]]'  # noqa: W605
    if selected:
        option = f'[{cursor_style}]{option}[/{cursor_style}]'
    return f'{prefix} {option}'


def update_rendered(live: Live, renderable: Union[ConsoleRenderable, str]) -> None:
    live.update(renderable=renderable)
    live.refresh()


def render(secure: bool, return_value: List[str], prompt: str, cursor_position: int, error: str, console: Console) -> str:
    render_value = (len(return_value) * '*' if secure else ''.join(return_value)) + ' '
    render_value = (
        render_value[:cursor_position]
        + '[black on white]'  # noqa: W503
        + render_value[cursor_position]  # noqa: W503
        + '[/black on white]'  # noqa: W503
        + render_value[(cursor_position + 1) :]  # noqa: W503,E203
    )
    render_value = f'{prompt}\n> {render_value}'
    if error:
        render_value = f'{render_value}\n[red]Error:[/red] {error}'
    return render_value


@contextmanager
def cursor_hidden(console: Console) -> Iterator:
    console.show_cursor(False)
    yield
    console.show_cursor(True)
