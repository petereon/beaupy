from unittest import mock

from beaupy import _beaupy as b
from yakh.key import Keys, Key
from ward import fixture, raises, test

from beaupy._internals import Abort
from beaupy._beaupy import Config, Live, select, warnings
import beaupy


def raise_keyboard_interrupt():
    raise KeyboardInterrupt()


@fixture
def set_raise_on_escape():
    Config.raise_on_escape = True
    yield
    Config.raise_on_escape = False


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


@test("`select` with 10 options")
def _():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8", "test9", "test10"])

    assert Live.update.call_args_list == [
        mock.call(renderable="[pink1]>[/pink1] test1\n  test2\n  test3\n  test4\n  test5\n  test6\n  test7\n  test8\n  test9\n  test10\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert Live.update.call_count == 1
    assert res == "test1"



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


@test("`select` raises Abort when ESC is pressed and raise_on_escape is True")
def _(set_raise_on_escape=set_raise_on_escape):
    steps = iter([Key("esc", (27,), is_printable=False)])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    with raises(Abort) as e:
        select(options=["test1", "test2", "test3", "test4"], cursor="x", cursor_style="green", cursor_index=1)
    assert str(e.raised) == "Aborted by user with key (27,)"


@test("`select` shows only the first 5 options and number of pages if pagination is enabled")
def _():
    steps = iter([Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(
        options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8"],
        cursor="x",
        cursor_style="green",
        pagination=True,
    )

    assert Live.update.call_args_list == [
        mock.call(
            renderable="[green]x[/green] test1\n  test2\n  test3\n  test4\n  test5[grey58]\n\nPage 1/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"
        ),
        mock.call(
            renderable="  test1\n[green]x[/green] test2\n  test3\n  test4\n  test5[grey58]\n\nPage 1/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"
        ),
        mock.call(
            renderable="  test1\n  test2\n[green]x[/green] test3\n  test4\n  test5[grey58]\n\nPage 1/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"
        ),
        mock.call(
            renderable="  test1\n  test2\n  test3\n[green]x[/green] test4\n  test5[grey58]\n\nPage 1/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"
        ),
    ]

    assert Live.update.call_count == 4
    assert res == "test4"


@test("`select` shows only the first 3 options and number of pages if pagination is enabled and page_size is 3")
def _():
    steps = iter([Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(
        options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8"],
        cursor="x",
        cursor_style="green",
        pagination=True,
        page_size=3,
    )

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/3[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n[green]x[/green] test2\n  test3[grey58]\n\nPage 1/3[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n  test2\n[green]x[/green] test3[grey58]\n\nPage 1/3[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert Live.update.call_count == 3
    assert res == "test3"


@test("`select` paginates forward when cursor is on the last option and `DOWN_ARROW` is pressed")
def _():
    steps = iter([Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(
        options=["test1", "test2", "test3", "test4", "test5"],
        cursor_index=2,
        cursor="x",
        cursor_style="green",
        pagination=True,
        page_size=3,
    )

    assert Live.update.call_args_list == [
        mock.call(renderable="  test1\n  test2\n[green]x[/green] test3[grey58]\n\nPage 1/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert Live.update.call_count == 2
    assert res == "test4"


@test("`select` paginates backward when cursor is on the first_option and second page and `UP_ARROW` is pressed")
def _():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(
        options=["test1", "test2", "test3", "test4", "test5"],
        cursor_index=3,
        cursor="x",
        cursor_style="green",
        pagination=True,
        page_size=3,
    )

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test1\n  test2\n[green]x[/green] test3[grey58]\n\nPage 1/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert Live.update.call_count == 2
    assert res == "test3"


@test("`select` paginates forward when `RIGHT_ARROW` is pressed")
def _():
    steps = iter([Keys.RIGHT_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4", "test5"], cursor="x", cursor_style="green", pagination=True, page_size=3)

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert Live.update.call_count == 2
    assert res == "test4"


@test("`select` paginates backwards when it's on second page `LEFT_ARROW` is pressed")
def _():
    steps = iter([Keys.LEFT_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(
        options=["test1", "test2", "test3", "test4", "test5"],
        cursor_index=3,
        cursor="x",
        cursor_style="green",
        pagination=True,
        page_size=3,
    )

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == "test1"


@test("`select` paginates to the first page when it's the last page and `RIGHT_ARROW` is pressed")
def _():
    steps = iter([Keys.RIGHT_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(
        options=["test1", "test2", "test3", "test4", "test5"],
        cursor_index=3,
        cursor="x",
        cursor_style="green",
        pagination=True,
        page_size=3,
    )

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == "test1"


@test("`select` paginates to the last page when it's the first page and `LEFT_ARROW` is pressed")
def _():
    steps = iter([Keys.LEFT_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4", "test5"], cursor="x", cursor_style="green", pagination=True, page_size=3)

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == "test4"


@test("`select` paginates to the first page when it's the last page and `HOME` is pressed")
def _():
    steps = iter([Keys.HOME, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(
        options=["test1", "test2", "test3", "test4", "test5"],
        cursor_index=3,
        cursor="x",
        cursor_style="green",
        pagination=True,
        page_size=3,
    )

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == "test1"


@test("`select` paginates to the last page when it's the first page and `END` is pressed")
def _():
    steps = iter([Keys.END, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(
        options=["test1", "test2", "test3", "test4", "test5"],
        cursor="x",
        cursor_style="green",
        pagination=True,
        page_size=3,
    )

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="  test4\n[green]x[/green] test5[grey58]\n\nPage 2/2[/grey58]\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == "test5"
