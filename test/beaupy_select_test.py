from unittest import mock

from beaupy import _beaupy as b
from yakh.key import Keys
from ward import raises, test

from beaupy._beaupy import Config, Live, select, warnings
import beaupy


def raise_keyboard_interrupt():
    raise KeyboardInterrupt()


@test("`select` with no options permissive")
def _():
    b.get_key = lambda: Keys.ENTER
    res = select(options=[])
    assert res == None


@test("`select` with no options strict")
def _():
    b.get_key = lambda: Keys.ENTER
    with raises(ValueError) as e:
        select(options=[], strict=True)

    assert str(e.raised) == "`options` cannot be empty"


@test("`select` with 1 option")
def _():
    steps = iter([Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    select(options=["test"])

    assert Live.update.call_args_list == [mock.call(renderable="[pink1]>[/pink1] test\n\n(Confirm with [bold]enter[/bold])")]

    assert Live.update.call_count == 1


@test("`select` with 1 option and down step")
def _():
    steps = iter([Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    select(options=["test"])

    assert Live.update.call_args_list == [
        mock.call(renderable="[pink1]>[/pink1] test\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="[pink1]>[/pink1] test\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2


@test("`select` with pressing end")
def _():
    steps = iter([Keys.END, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"])

    assert Live.update.call_args_list == [
        mock.call(renderable="[pink1]>[/pink1] test1\n  test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n  test2\n  test3\n[pink1]>[/pink1] test4\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert Live.update.call_count == 2
    assert res == "test4"


@test("`select` with pressing down twice and selecting first with home")
def _():
    steps = iter([Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.HOME, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"])

    assert Live.update.call_args_list == [
        mock.call(renderable="[pink1]>[/pink1] test1\n  test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n[pink1]>[/pink1] test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n  test2\n[pink1]>[/pink1] test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="[pink1]>[/pink1] test1\n  test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert Live.update.call_count == 4
    assert res == "test1"


@test("`select` with 4 options stepping down through all with random character inbetween and selecting last")
def _():
    steps = iter(
        [
            Keys.DOWN_ARROW,
            Keys.DOWN_ARROW,
            "h",
            Keys.DOWN_ARROW,
            Keys.ENTER,
        ]
    )

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"])

    assert Live.update.call_args_list == [
        mock.call(renderable="[pink1]>[/pink1] test1\n  test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n[pink1]>[/pink1] test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n  test2\n[pink1]>[/pink1] test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n  test2\n[pink1]>[/pink1] test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n  test2\n  test3\n[pink1]>[/pink1] test4\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert Live.update.call_count == 5
    assert res == "test4"


@test(
    "`select` with 4 options stepping down through all and selecting last with `x` as a cursor and `green` as a cursor color",
)
def _():
    steps = iter([Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"], cursor="x", cursor_style="green")

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n[green]x[/green] test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n  test2\n[green]x[/green] test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n  test2\n  test3\n[green]x[/green] test4\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 4
    assert res == "test4"


@test("`select` with 4 options stepping up and selecting last with `x` as a cursor and `green` as a cursor color")
def _():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"], cursor="x", cursor_style="green")

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n  test2\n  test3\n[green]x[/green] test4\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == "test4"


@test("`select` with 4 options stepping up and selecting last with `x` as a cursor and `green` as a cursor color")
def _():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"], cursor="x", cursor_style="green", cursor_index=1)

    assert Live.update.call_args_list == [
        mock.call(renderable="  test1\n[green]x[/green] test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == "test1"


@test(
    "`select` with 4 options calling `Ctrl+C` with `x` as a cursor and `green` as a cursor color and with raise on keyboard interrupt False",
)
def _():
    Live.update = mock.MagicMock()
    Config.raise_on_interrupt = False
    b.get_key = lambda: Keys.CTRL_C
    res = select(
        options=["test1", "test2", "test3", "test4"],
        cursor="x",
        cursor_style="green",
        cursor_index=1,
    )

    assert Live.update.call_args_list == [
        mock.call(renderable="  test1\n[green]x[/green] test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])")
    ]
    assert Live.update.call_count == 1
    assert res == None


@test(
    "`select` with 4 options stepping down through all and selecting last with `x` as a cursor, `green` as a cursor color and returning index instead of value",
)
def _():
    steps = iter([Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(
        options=["test1", "test2", "test3", "test4"],
        cursor="x",
        cursor_style="green",
        return_index=True,
    )

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n[green]x[/green] test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n  test2\n[green]x[/green] test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n  test2\n  test3\n[green]x[/green] test4\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert Live.update.call_count == 4
    assert res == 3


@test(
    "`select` with 4 options calling `Ctrl+C` with `x` as a cursor and `green` as a cursor color and with raise on keyboard interrupt True",
)
def _():
    Config.raise_on_interrupt = True
    b.get_key = lambda: Keys.CTRL_C
    with raises(KeyboardInterrupt):
        select(
            options=["test1", "test2", "test3", "test4"],
            cursor="x",
            cursor_style="green",
            cursor_index=1,
        )


@test("`select` with 2 options and invalid cursor style")
def _():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    warnings.warn = mock.MagicMock()
    select(options=["test1", "test2"], cursor_style="")
    warnings.warn.assert_called_once_with("`cursor_style` should be a valid style, defaulting to `white`")


@test(
    "`select` with 4 options stepping down through all and selecting last with `x` as a cursor, `green` as a cursor color and returning index instead of value and preprocessor selecting the last element",
)
def _():
    steps = iter([Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(
        options=["test1", "test2", "test3", "test4"],
        preprocessor=lambda val: val[-1],
        cursor="x",
        cursor_style="green",
        return_index=True,
    )

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] 1\n  2\n  3\n  4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  1\n[green]x[/green] 2\n  3\n  4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  1\n  2\n[green]x[/green] 3\n  4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  1\n  2\n  3\n[green]x[/green] 4\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert Live.update.call_count == 4
    assert res == 3

@test("`select` returns none when ESC is pressed")
def _():
    steps = iter([Keys.ESC])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"], cursor="x", cursor_style="green", cursor_index=1)

    assert Live.update.call_args_list == [
        mock.call(renderable="  test1\n[green]x[/green] test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 1
    assert res == None