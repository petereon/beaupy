from unittest import mock

import readchar
from ward import raises, test

from beaupy._beaupy import Config, Live, select, warnings


@test("`select` with no options permissive", tags=["v1", "select"])
def _():
    readchar.readkey = lambda: readchar.key.ENTER
    res = select(options=[])
    assert res == None


@test("`select` with no options strict", tags=["v1", "select"])
def _():
    readchar.readkey = lambda: readchar.key.ENTER
    with raises(ValueError) as e:
        select(options=[], strict=True)

    assert str(e.raised) == "`options` cannot be empty"


@test("`select` with 1 option", tags=["v1", "select"])
def _():
    steps = iter([readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    select(options=["test"])

    assert Live.update.call_args_list == [mock.call(renderable="[pink1]>[/pink1] test\n\n(Confirm with [bold]enter[/bold])")]

    assert Live.update.call_count == 1


@test("`select` with 1 option and down step", tags=["v1", "select"])
def _():
    steps = iter([readchar.key.DOWN, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    select(options=["test"])

    assert Live.update.call_args_list == [
        mock.call(renderable="[pink1]>[/pink1] test\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="[pink1]>[/pink1] test\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2


@test("`select` with 4 options stepping down through all with random character inbetween and selecting last", tags=["v1", "select"])
def _():
    steps = iter(
        [
            readchar.key.DOWN,
            readchar.key.DOWN,
            "h",
            readchar.key.DOWN,
            readchar.key.ENTER,
        ]
    )

    readchar.readkey = lambda: next(steps)
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
    tags=["v1", "select"],
)
def _():
    steps = iter([readchar.key.DOWN, readchar.key.DOWN, readchar.key.DOWN, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
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


@test("`select` with 4 options stepping up and selecting last with `x` as a cursor and `green` as a cursor color", tags=["v1", "select"])
def _():
    steps = iter([readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"], cursor="x", cursor_style="green")

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3\n  test4\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == "test1"


@test("`select` with 4 options stepping up and selecting last with `x` as a cursor and `green` as a cursor color", tags=["v1", "select"])
def _():
    steps = iter([readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
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
    tags=["v1", "select"],
)
def _():
    steps = iter([readchar.key.CTRL_C])

    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    Config.raise_on_interrupt = False
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
    tags=["v1", "select"],
)
def _():
    steps = iter([readchar.key.DOWN, readchar.key.DOWN, readchar.key.DOWN, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
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
    tags=["v1", "select"],
)
def _():
    steps = iter([readchar.key.CTRL_C])
    Config.raise_on_interrupt = True
    readchar.readkey = lambda: next(steps)
    with raises(KeyboardInterrupt) as ex:
        select(
            options=["test1", "test2", "test3", "test4"],
            cursor="x",
            cursor_style="green",
            cursor_index=1,
        )
    assert ex.raised.args[0] == readchar.key.CTRL_C


@test("`select` with 2 options and invalid cursor style", tags=["v1", "select"])
def _():
    steps = iter([readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    warnings.warn = mock.MagicMock()
    select(options=["test1", "test2"], cursor_style="")
    warnings.warn.assert_called_once_with("`cursor_style` should be a valid style, defaulting to `white`")


@test(
    "`select` with 4 options stepping down through all and selecting last with `x` as a cursor, `green` as a cursor color and returning index instead of value and preprocessor selecting the last element",
    tags=["select"],
)
def _():
    steps = iter([readchar.key.DOWN, readchar.key.DOWN, readchar.key.DOWN, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
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
