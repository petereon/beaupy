from contextlib import contextmanager
from sys import stdout
from typing import Iterator, List

import emoji
from rich.console import Console


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


def reset_lines(num_lines: int) -> None:
    stdout.write(f'\x1b[{num_lines}F\x1b[0J')


def render(secure: bool, return_value: List[str], prompt: str, cursor_position: int, console: Console) -> None:
    render_value = (len(return_value) * '*' if secure else ''.join(return_value)) + ' '
    render_value = (
        render_value[:cursor_position]
        + '[black on white]'  # noqa: W503
        + render_value[cursor_position]  # noqa: W503
        + '[/black on white]'  # noqa: W503
        + render_value[(cursor_position + 1) :]  # noqa: W503,E203
    )
    console.print(f'{prompt}\n> {render_value}')
    reset_lines(2)


def hide_cursor() -> None:
    stdout.write('\x1b[?25l')


def show_cursor() -> None:
    stdout.write('\x1b[?25h')


@contextmanager
def cursor_hidden() -> Iterator:
    hide_cursor()
    yield
    show_cursor()
