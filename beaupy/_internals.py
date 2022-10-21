from contextlib import contextmanager
from typing import Iterator, List, Union

import emoji
from rich.console import Console, ConsoleRenderable
from rich.live import Live


class ValidationError(Exception):
    pass


class ConversionError(Exception):
    pass


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


def _render_prompt(secure: bool, typed_values: List[str], prompt: str, cursor_position: int, error: str, multiline: bool = False) -> str:
    render_value = (len(typed_values) * '*' if secure else ''.join(typed_values)) + ' '
    render_value = (
        render_value[:cursor_position]
        + '[black on white]'  # noqa: W503
        + render_value[cursor_position]  # noqa: W503
        + '[/black on white]'  # noqa: W503
        + render_value[(cursor_position + 1) :]  # noqa: W503,E203
    )
    render_value = '\n> '.join(render_value.splitlines(keepends=True))
    if multiline:
        confirm_msg = '(Use [bold]enter[/bold] to insert a new line. Confirm with [bold]alt-enter[/bold])'
    else:
        confirm_msg = '(Confirm with [bold]enter[/bold])'
    render_value = f'{prompt}\n> {render_value}\n\n{confirm_msg}'
    if error:
        render_value = f'{render_value}\n[red]Error:[/red] {error}'
    return render_value


@contextmanager
def _cursor_hidden(console: Console) -> Iterator:
    console.show_cursor(False)
    yield
    console.show_cursor(True)
