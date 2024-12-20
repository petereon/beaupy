from unittest import mock
import pytest

from beaupy import _beaupy as b
from yakh.key import Keys, Key

from beaupy._internals import Abort
from beaupy._beaupy import Config, Live, select, warnings


def raise_keyboard_interrupt():
    raise KeyboardInterrupt()


@pytest.fixture
def set_raise_on_escape():
    Config.raise_on_escape = True
    yield
    Config.raise_on_escape = False


def test_select_with_no_options_permissive():
    b.get_key = lambda: Keys.ENTER
    res = select(options=[])
    assert res is None

def test_select_with_no_options_strict():
    b.get_key = lambda: Keys.ENTER
    with pytest.raises(ValueError) as e:
        select(options=[], strict=True)

    assert str(e.value) == "`options` cannot be empty"


def test_select_with_one_option():
    steps = iter([Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    select(options=["test"])

    assert Live.update.call_args_list == [mock.call(renderable="[pink1]>[/pink1] test\n\n([bold]enter[/bold] to confirm)")]

    assert Live.update.call_count == 1


def test_select_with_one_option_and_down_step():
    steps = iter([Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    select(options=["test"])

    assert Live.update.call_args_list == [
        mock.call(renderable="[pink1]>[/pink1] test\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="[pink1]>[/pink1] test\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2


def test_select_with_pressing_end():
    steps = iter([Keys.END, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"])

    assert Live.update.call_args_list == [
        mock.call(renderable="[pink1]>[/pink1] test1\n  test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n  test3\n[pink1]>[/pink1] test4\n\n([bold]enter[/bold] to confirm)"),
    ]

    assert Live.update.call_count == 2
    assert res == "test4"


def test_select_with_ten_options_stepping_through_them():
    steps = iter([Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW ,Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8", "test9", "test10"])

    assert Live.update.call_args_list == [
        mock.call(renderable="[pink1]>[/pink1] test1\n  test2\n  test3\n  test4\n  test5\n  test6\n  test7\n  test8\n  test9\n  test10\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n[pink1]>[/pink1] test2\n  test3\n  test4\n  test5\n  test6\n  test7\n  test8\n  test9\n  test10\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n[pink1]>[/pink1] test3\n  test4\n  test5\n  test6\n  test7\n  test8\n  test9\n  test10\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n  test3\n[pink1]>[/pink1] test4\n  test5\n  test6\n  test7\n  test8\n  test9\n  test10\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n  test3\n  test4\n[pink1]>[/pink1] test5\n  test6\n  test7\n  test8\n  test9\n  test10\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n  test3\n  test4\n  test5\n[pink1]>[/pink1] test6\n  test7\n  test8\n  test9\n  test10\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n  test3\n  test4\n  test5\n  test6\n[pink1]>[/pink1] test7\n  test8\n  test9\n  test10\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n  test3\n  test4\n  test5\n  test6\n  test7\n[pink1]>[/pink1] test8\n  test9\n  test10\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n  test3\n  test4\n  test5\n  test6\n  test7\n  test8\n[pink1]>[/pink1] test9\n  test10\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n  test3\n  test4\n  test5\n  test6\n  test7\n  test8\n  test9\n[pink1]>[/pink1] test10\n\n([bold]enter[/bold] to confirm)"),
    ]

    assert Live.update.call_count == 10
    assert res == "test10"


def test_select_with_pressing_down_twice_and_selecting_first_with_home():
    steps = iter([Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.HOME, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"])

    assert Live.update.call_args_list == [
        mock.call(renderable="[pink1]>[/pink1] test1\n  test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n[pink1]>[/pink1] test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n[pink1]>[/pink1] test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="[pink1]>[/pink1] test1\n  test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
    ]

    assert Live.update.call_count == 4
    assert res == "test1"


def test_select_with_four_options_stepping_down_with_random_character_inbetween_and_selecting_last():
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
        mock.call(renderable="[pink1]>[/pink1] test1\n  test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n[pink1]>[/pink1] test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n[pink1]>[/pink1] test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n  test3\n[pink1]>[/pink1] test4\n\n([bold]enter[/bold] to confirm)"),
    ]

    assert Live.update.call_count == 4
    assert res == "test4"
def test_select_with_4_options_stepping_down_and_selecting_last():
    steps = iter([Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"], cursor="x", cursor_style="green")

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n[green]x[/green] test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n[green]x[/green] test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n  test3\n[green]x[/green] test4\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 4
    assert res == "test4"


def test_select_with_4_options_stepping_up_and_selecting_last():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"], cursor="x", cursor_style="green")

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n  test3\n[green]x[/green] test4\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res == "test4"


def test_select_with_4_options_stepping_up_and_selecting_first():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"], cursor="x", cursor_style="green", cursor_index=1)

    assert Live.update.call_args_list == [
        mock.call(renderable="  test1\n[green]x[/green] test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res == "test1"


def test_select_with_4_options_ctrl_c_no_raise():
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
        mock.call(renderable="  test1\n[green]x[/green] test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)")
    ]
    assert Live.update.call_count == 1
    assert res is None


def test_select_with_4_options_stepping_down_and_selecting_last_return_index():
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
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n[green]x[/green] test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n[green]x[/green] test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n  test3\n[green]x[/green] test4\n\n([bold]enter[/bold] to confirm)"),
    ]

    assert Live.update.call_count == 4
    assert res == 3


def test_select_with_4_options_ctrl_c_raise():
    Config.raise_on_interrupt = True
    b.get_key = lambda: Keys.CTRL_C
    with pytest.raises(KeyboardInterrupt):
        select(
            options=["test1", "test2", "test3", "test4"],
            cursor="x",
            cursor_style="green",
            cursor_index=1,
        )


def test_select_with_2_options_invalid_cursor_style():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    warnings.warn = mock.MagicMock()
    select(options=["test1", "test2"], cursor_style="")
    warnings.warn.assert_called_once_with("`cursor_style` should be a valid style, defaulting to `white`")


def test_select_with_4_options_preprocessor():
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
        mock.call(renderable="[green]x[/green] 1\n  2\n  3\n  4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  1\n[green]x[/green] 2\n  3\n  4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  1\n  2\n[green]x[/green] 3\n  4\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  1\n  2\n  3\n[green]x[/green] 4\n\n([bold]enter[/bold] to confirm)"),
    ]

    assert Live.update.call_count == 4
    assert res == 3

def test_select_returns_none_when_esc_is_pressed():
    steps = iter([Keys.ESC])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4"], cursor="x", cursor_style="green", cursor_index=1)

    assert Live.update.call_args_list == [
        mock.call(renderable="  test1\n[green]x[/green] test2\n  test3\n  test4\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 1
    assert res is None


def test_select_raises_abort_when_esc_is_pressed_and_raise_on_escape_is_true(set_raise_on_escape):
    steps = iter([Key("esc", (27,), is_printable=False)])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    with pytest.raises(Abort) as e:
        select(options=["test1", "test2", "test3", "test4"], cursor="x", cursor_style="green", cursor_index=1)
    assert str(e.value) == "Aborted by user with key (27,)"


def test_select_shows_only_first_5_options_and_number_of_pages_if_pagination_is_enabled():
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
            renderable="[green]x[/green] test1\n  test2\n  test3\n  test4\n  test5[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="  test1\n[green]x[/green] test2\n  test3\n  test4\n  test5[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="  test1\n  test2\n[green]x[/green] test3\n  test4\n  test5[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="  test1\n  test2\n  test3\n[green]x[/green] test4\n  test5[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"
        ),
    ]

    assert Live.update.call_count == 4
    assert res == "test4"


def test_select_shows_only_first_3_options_and_number_of_pages_if_pagination_is_enabled_and_page_size_is_3():
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
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/3[/grey58]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n[green]x[/green] test2\n  test3[grey58]\n\nPage 1/3[/grey58]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n[green]x[/green] test3[grey58]\n\nPage 1/3[/grey58]\n\n([bold]enter[/bold] to confirm)"),
    ]

    assert Live.update.call_count == 3
    assert res == "test3"


def test_select_paginates_forward_when_cursor_is_on_last_option_and_down_arrow_is_pressed():
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
        mock.call(renderable="  test1\n  test2\n[green]x[/green] test3[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
    ]

    assert Live.update.call_count == 2
    assert res == "test4"


def test_select_paginates_backward_when_cursor_is_on_first_option_and_second_page_and_up_arrow_is_pressed():
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
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test1\n  test2\n[green]x[/green] test3[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
    ]

    assert Live.update.call_count == 2
    assert res == "test3"


def test_select_paginates_forward_when_right_arrow_is_pressed():
    steps = iter([Keys.RIGHT_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4", "test5"], cursor="x", cursor_style="green", pagination=True, page_size=3)

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
    ]

    assert Live.update.call_count == 2
    assert res == "test4"


def test_select_paginates_backward_when_on_second_page_and_left_arrow_is_pressed():
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
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res == "test1"


def test_select_paginates_to_first_page_when_on_last_page_and_right_arrow_is_pressed():
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
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res == "test1"


def test_select_paginates_to_last_page_when_on_first_page_and_left_arrow_is_pressed():
    steps = iter([Keys.LEFT_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select(options=["test1", "test2", "test3", "test4", "test5"], cursor="x", cursor_style="green", pagination=True, page_size=3)

    assert Live.update.call_args_list == [
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res == "test4"


def test_select_paginates_to_first_page_when_on_last_page_and_home_is_pressed():
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
        mock.call(renderable="[green]x[/green] test4\n  test5[grey58]\n\nPage 2/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res == "test1"


def test_select_paginates_to_last_page_when_on_first_page_and_end_is_pressed():
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
        mock.call(renderable="[green]x[/green] test1\n  test2\n  test3[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="  test4\n[green]x[/green] test5[grey58]\n\nPage 2/2[/grey58]\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res == "test5"
