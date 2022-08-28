import sys

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
    for _ in range(num_lines):
        sys.stdout.write('\x1b[2K\033[F\x1b[2K')


def render(secure: bool, return_value: str, prompt: str, console: Console) -> None:
    render_value = len(return_value) * '*' if secure else return_value
    console.print(f'{prompt}\n> {render_value}')
    reset_lines(2)
