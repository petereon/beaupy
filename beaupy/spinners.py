from itertools import cycle
from typing import List

from rich.live import Live

ARC = ['◜', '◠', '◝', '◞', '◡', '◟']
ARROWS = ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙']
BARS = ['▁', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃']
CLOCK = ['🕛 ', '🕐 ', '🕑 ', '🕒 ', '🕓 ', '🕔 ', '🕕 ', '🕖 ', '🕗 ', '🕘 ', '🕙 ', '🕚 ']
DIAMOND = ['◇', '◈', '◆']
DOT = ['⠁', '⠂', '⠄', '⡀', '⢀', '⠠', '⠐', '⠈']
DOTS = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
LINE = ['|', '/', '-', '\\']
LOADING = ['l      ', 'lo     ', 'loa    ', 'load   ', 'loadi  ', 'loadin ', 'loading']
MOON = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']


class CustomSpinner:
    _spinner_characters: cycle
    _live_display: Live

    def __init__(self, spinner_characters: List[str], text: str, refresh_per_second: float = 4, transient: bool = True):
        if len(spinner_characters) == 0:
            raise ValueError('`spinner_characters` can\'t be empty')
        self._spinner_characters = cycle(spinner_characters)
        self._live_display = Live(
            '',
            transient=transient,
            refresh_per_second=refresh_per_second,
            get_renderable=lambda: f'{next(self._spinner_characters)} {text}',
        )

    def start(self) -> None:
        self._live_display.start()

    def stop(self) -> None:
        self._live_display.stop()
