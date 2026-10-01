from itertools import cycle
from typing import Optional, Sequence

from rich.console import Console
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


class Spinner:
    _spinner_characters: cycle
    _live_display: Live

    def __init__(
        self,
        spinner_characters: Sequence[str] = DOTS,
        *,
        text: str = 'Loading...',
        refresh_per_second: float = 10,
        transient: bool = True,
        console: Optional[Console] = None,
    ):
        """Creates a spinner which can be used to provide some user feedback during long processing

        Can be used as a context manager, which also stops the spinner if the body raises:
        `with Spinner(DOTS, text='Working...'): do_work()`

        Args:
            spinner_characters (Sequence[str]): Strings that will be displayed in sequence by a spinner. Defaults to `DOTS`.
            text (str): Static text that will be shown after the spinner. Defaults to `Loading...`
            refresh_per_second (float, optional): Number of refreshes the spinner will do a second, this will affect
                                                  the fluidity of the "animation". Defaults to 10.
            transient (bool, optional): If the spinner will disappear after it's done, otherwise not. Defaults to True.
            console (rich.console.Console, optional): Console to render to, e.g. the one passed to elements via `Config`.
                                                      Defaults to Rich's global console.

        Raises:
            ValueError: Raised when no `spinner_characters` are provided in
        """
        if len(spinner_characters) == 0:
            raise ValueError("`spinner_characters` can't be empty")
        self._spinner_characters = cycle(spinner_characters)
        self._live_display = Live(
            '',
            console=console,
            transient=transient,
            refresh_per_second=refresh_per_second,
            get_renderable=lambda: f'{next(self._spinner_characters)} {text}',
        )

    def start(self) -> None:
        """Starts the spinner"""
        self._live_display.start()

    def stop(self) -> None:
        """Stops the spinner"""
        self._live_display.stop()

    def __enter__(self) -> 'Spinner':
        self.start()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.stop()
