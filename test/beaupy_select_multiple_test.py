from unittest import mock
import pytest

from beaupy import _beaupy as b
from yakh.key import Keys, Key

from beaupy._internals import Abort

from beaupy._beaupy import Config, Live, select_multiple, warnings


def raise_keyboard_interrupt():
    raise KeyboardInterrupt()


@pytest.fixture
def set_raise_on_escape():
    Config.raise_on_escape = True
    yield
    Config.raise_on_escape = False


def test_select_multiple_with_no_options_permissive():
    b.get_key = lambda: Keys.ENTER
    res = select_multiple(options=[])
    assert res == []


def test_select_multiple_with_no_options_strict():
    b.get_key = lambda: Keys.ENTER
    with pytest.raises(ValueError) as e:
        select_multiple(options=[], strict=True)

    assert str(e.value) == "`options` cannot be empty"

def test_select_multiple_with_2_options_selecting_down():
    steps = iter([" ", Keys.DOWN_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋")
    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[[pink1]😋[/pink1]] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 4
    assert res == ["test1", "test2"]


def test_select_multiple_with_2_options_pressing_escape():
    steps = iter([Keys.ESC])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋")
    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 1
    assert res == []


def test_select_multiple_with_10_options_stepping_through():
    steps = iter([Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.ESC])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8", "test9", "test10"], tick_character="😋")
    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\\[  ] test3\n\\[  ] test4\n\\[  ] test5\n\\[  ] test6\n\\[  ] test7\n\\[  ] test8\n\\[  ] test9\n\\[  ] test10\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] test1\n\\[  ] [pink1]test2[/pink1]\n\\[  ] test3\n\\[  ] test4\n\\[  ] test5\n\\[  ] test6\n\\[  ] test7\n\\[  ] test8\n\\[  ] test9\n\\[  ] test10\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] test1\n\\[  ] test2\n\\[  ] [pink1]test3[/pink1]\n\\[  ] test4\n\\[  ] test5\n\\[  ] test6\n\\[  ] test7\n\\[  ] test8\n\\[  ] test9\n\\[  ] test10\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] test1\n\\[  ] test2\n\\[  ] test3\n\\[  ] [pink1]test4[/pink1]\n\\[  ] test5\n\\[  ] test6\n\\[  ] test7\n\\[  ] test8\n\\[  ] test9\n\\[  ] test10\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] test1\n\\[  ] test2\n\\[  ] test3\n\\[  ] test4\n\\[  ] [pink1]test5[/pink1]\n\\[  ] test6\n\\[  ] test7\n\\[  ] test8\n\\[  ] test9\n\\[  ] test10\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] test1\n\\[  ] test2\n\\[  ] test3\n\\[  ] test4\n\\[  ] test5\n\\[  ] [pink1]test6[/pink1]\n\\[  ] test7\n\\[  ] test8\n\\[  ] test9\n\\[  ] test10\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] test1\n\\[  ] test2\n\\[  ] test3\n\\[  ] test4\n\\[  ] test5\n\\[  ] test6\n\\[  ] [pink1]test7[/pink1]\n\\[  ] test8\n\\[  ] test9\n\\[  ] test10\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] test1\n\\[  ] test2\n\\[  ] test3\n\\[  ] test4\n\\[  ] test5\n\\[  ] test6\n\\[  ] test7\n\\[  ] [pink1]test8[/pink1]\n\\[  ] test9\n\\[  ] test10\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] test1\n\\[  ] test2\n\\[  ] test3\n\\[  ] test4\n\\[  ] test5\n\\[  ] test6\n\\[  ] test7\n\\[  ] test8\n\\[  ] [pink1]test9[/pink1]\n\\[  ] test10\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] test1\n\\[  ] test2\n\\[  ] test3\n\\[  ] test4\n\\[  ] test5\n\\[  ] test6\n\\[  ] test7\n\\[  ] test8\n\\[  ] test9\n\\[  ] [pink1]test10[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 10
    assert res == []


def test_select_multiple_with_2_options_selecting_down_and_up():
    steps = iter([" ", Keys.DOWN_ARROW, " ", Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋")
    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[[pink1]😋[/pink1]] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[[pink1]😋[/pink1]] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 5
    assert res == ["test1", "test2"]

def test_select_multiple_with_2_options_starting_from_first_selecting_going_up_and_selecting_again():
    steps = iter([" ", Keys.UP_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋")
    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[[pink1]😋[/pink1]] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 4
    assert res == ["test1", "test2"]


def test_select_multiple_with_2_options_starting_from_first_selecting_going_down_and_selecting_second_also_with_return_indices_as_True():
    steps = iter([" ", Keys.DOWN_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋", return_indices=True)
    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[[pink1]😋[/pink1]] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 4
    assert res == [0, 1]


def test_select_multiple_with_moving_down_then_pressing_home_and_selecting_first():
    steps = iter([Keys.DOWN_ARROW, Keys.HOME, " ", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋")

    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] test1\n\\[  ] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]

    assert Live.update.call_count == 4
    assert res == ["test1"]


def test_select_multiple_with_pressing_end_and_selecting_last():
    steps = iter([Keys.END, " ", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋")

    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] test1\n\\[  ] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[  ] test1\n\\[[pink1]😋[/pink1]] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]

    assert Live.update.call_count == 3
    assert res == ["test2"]

def test_select_multiple_with_2_options_tick_character_and_color():
    steps = iter([" ", Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(
        options=["test1", "test2"],
        tick_character="x",
        tick_style="yellow1",
        cursor_index=1,
    )
    assert Live.update.call_args_list == [
        mock.call(renderable="\\[ ] test1\n\\[ ] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"),
        mock.call(
            renderable="\\[ ] test1\n\\[[yellow1]x[/yellow1]] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] [pink1]test1[/pink1]\n\\[[yellow1]x[/yellow1]] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 3
    assert res == ["test2"]


def test_select_multiple_with_2_options_tick_character_and_color_with_preselected():
    steps = iter([" ", Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(
        options=["test1", "test2"],
        tick_character="x",
        tick_style="yellow1",
        cursor_index=1,
        ticked_indices=[0],
    )
    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[[yellow1]x[/yellow1]] test1\n\\[ ] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[yellow1]x[/yellow1]] test1\n\\[[yellow1]x[/yellow1]] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[yellow1]x[/yellow1]] [pink1]test1[/pink1]\n\\[[yellow1]x[/yellow1]] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 3
    assert res == ["test1", "test2"]


def test_select_multiple_with_maximal_count():
    steps = iter([" ", Keys.DOWN_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋", maximal_count=1)

    assert Live.update.call_args_list[:4] == [
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)\n[red]Error:[/red] Must select at most 1 options"
        ),
    ]
    assert Live.update.call_count == 4
    assert res == ["test1"]


def test_select_multiple_with_minimal_count():
    steps = iter(
        [
            " ",
            Keys.DOWN_ARROW,
            Keys.ENTER,
            " ",
            Keys.ENTER,
        ]
    )

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋", minimal_count=2)
    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)\n[red]Error:[/red] Must select at least 2 options"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[[pink1]😋[/pink1]] [pink1]test2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 5
    assert res == ["test1", "test2"]

def test_select_multiple_with_2_options_and_calling_ctrl_c_with_raise_on_keyboard_interrupt_false():
    Config.raise_on_interrupt = False
    Live.update = mock.MagicMock()
    b.get_key = lambda: Keys.CTRL_C
    res = select_multiple(options=["test1", "test2"], tick_character="😋")
    assert Live.update.call_args_list == [
        mock.call(renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)")
    ]
    assert Live.update.call_count == 1
    assert res == []


def test_select_multiple_with_2_options_and_calling_ctrl_c_with_raise_on_keyboard_interrupt_true():
    Config.raise_on_interrupt = True
    Live.update = mock.MagicMock()
    b.get_key = lambda: Keys.CTRL_C
    with pytest.raises(KeyboardInterrupt):
        select_multiple(options=["test1", "test2"], tick_character="😋")


def test_select_multiple_with_2_options_and_invalid_tick_style():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    warnings.warn = mock.MagicMock()
    select_multiple(options=["test1", "test2"], tick_style="")
    warnings.warn.assert_called_once_with("`tick_style` should be a valid style, defaulting to `white`")


def test_select_multiple_with_2_options_and_invalid_cursor_style():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    warnings.warn = mock.MagicMock()
    select_multiple(options=["test1", "test2"], cursor_style="")
    warnings.warn.assert_called_once_with("`cursor_style` should be a valid style, defaulting to `white`")


def test_select_multiple_with_2_options_starting_from_first_selecting_going_down_and_selecting_second_then_deselecting_with_preprocessor():
    steps = iter([" ", Keys.DOWN_ARROW, " ", " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋", preprocessor=lambda val: val[-1])
    assert Live.update.call_args_list == [
        mock.call(renderable="\\[  ] [pink1]1[/pink1]\n\\[  ] 2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] [pink1]1[/pink1]\n\\[  ] 2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] 1\n\\[  ] [pink1]2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] 1\n\\[[pink1]😋[/pink1]] [pink1]2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] 1\n\\[  ] [pink1]2[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 5
    assert res == ["test1"]


def test_select_multiple_returns_empty_when_esc_is_pressed():
    steps = iter([" ", Keys.ESC])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋", return_indices=True)
    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] test2\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 2
    assert res == []


def test_select_multiple_raises_abort_when_esc_is_pressed_and_raise_on_escape_is_true(set_raise_on_escape):
    steps = iter([Key("esc", (27,), is_printable=False)])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    with pytest.raises(Abort) as e:
        select_multiple(options=["test1", "test2"], tick_character="😋")
    assert str(e.value) == "Aborted by user with key (27,)"


def test_select_multiple_shows_only_5_options_if_pagination_is_enabled():
    steps = iter([Keys.DOWN_ARROW, Keys.DOWN_ARROW, Keys.DOWN_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(
        options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8"],
        cursor_style="green",
        pagination=True,
    )

    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[ ] [green]test1[/green]\n\\[ ] test2\n\\[ ] test3\n\\[ ] test4\n\\[ ] test5[grey58]\n\nPage 1/2[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] test1\n\\[ ] [green]test2[/green]\n\\[ ] test3\n\\[ ] test4\n\\[ ] test5[grey58]\n\nPage 1/2[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] test1\n\\[ ] test2\n\\[ ] [green]test3[/green]\n\\[ ] test4\n\\[ ] test5[grey58]\n\nPage 1/2[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] test1\n\\[ ] test2\n\\[ ] test3\n\\[ ] [green]test4[/green]\n\\[ ] test5[grey58]\n\nPage 1/2[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] test1\n\\[ ] test2\n\\[ ] test3\n\\[[pink1]✓[/pink1]] [green]test4[/green]\n\\[ ] test5[grey58]\n\nPage 1/2[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]

    assert Live.update.call_count == 5
    assert res == ["test4"]

def test_select_multiple_shows_only_3_options_if_pagination_is_enabled_and_page_size_is_3():
    steps = iter([Keys.DOWN_ARROW, Keys.DOWN_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(
        options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8"],
        cursor_style="green",
        pagination=True,
        page_size=3,
    )

    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[ ] [green]test1[/green]\n\\[ ] test2\n\\[ ] test3[grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] test1\n\\[ ] [green]test2[/green]\n\\[ ] test3[grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] test1\n\\[ ] test2\n\\[ ] [green]test3[/green][grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] test1\n\\[ ] test2\n\\[[pink1]✓[/pink1]] [green]test3[/green][grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]

    assert Live.update.call_count == 4
    assert res == ["test3"]


def test_select_multiple_paginates_forwards_if_last_option_is_selected_and_down_arrow_is_pressed():
    steps = iter([Keys.DOWN_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(
        options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8"],
        cursor_style="green",
        pagination=True,
        page_size=3,
        cursor_index=2,
    )

    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[ ] test1\n\\[ ] test2\n\\[ ] [green]test3[/green][grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] [green]test4[/green]\n\\[ ] test5\n\\[ ] test6[grey58]\n\nPage 2/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]✓[/pink1]] [green]test4[/green]\n\\[ ] test5\n\\[ ] test6[grey58]\n\nPage 2/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]

    assert Live.update.call_count == 3
    assert res == ["test4"]


def test_select_multiple_paginates_backwards_if_first_option_is_selected_on_second_page_and_up_arrow_is_pressed():
    steps = iter([Keys.UP_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(
        options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8"],
        cursor_style="green",
        pagination=True,
        page_size=3,
        cursor_index=3,
    )

    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[ ] [green]test4[/green]\n\\[ ] test5\n\\[ ] test6[grey58]\n\nPage 2/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] test1\n\\[ ] test2\n\\[ ] [green]test3[/green][grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] test1\n\\[ ] test2\n\\[[pink1]✓[/pink1]] [green]test3[/green][grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]

    assert Live.update.call_count == 3
    assert res == ["test3"]


def test_select_multiple_paginates_backwards_if_on_second_page_and_left_arrow_is_pressed():
    steps = iter([Keys.LEFT_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(
        options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8"],
        cursor_style="green",
        pagination=True,
        page_size=3,
        cursor_index=3,
    )

    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[ ] [green]test4[/green]\n\\[ ] test5\n\\[ ] test6[grey58]\n\nPage 2/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] [green]test1[/green]\n\\[ ] test2\n\\[ ] test3[grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]✓[/pink1]] [green]test1[/green]\n\\[ ] test2\n\\[ ] test3[grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]

    assert Live.update.call_count == 3
    assert res == ["test1"]

def test_select_multiple_paginates_forwards_if_on_first_page_and_right_arrow_is_pressed():
    steps = iter([Keys.RIGHT_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(
        options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8"],
        cursor_style="green",
        pagination=True,
        page_size=3,
    )

    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[ ] [green]test1[/green]\n\\[ ] test2\n\\[ ] test3[grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] [green]test4[/green]\n\\[ ] test5\n\\[ ] test6[grey58]\n\nPage 2/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]✓[/pink1]] [green]test4[/green]\n\\[ ] test5\n\\[ ] test6[grey58]\n\nPage 2/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]

    assert Live.update.call_count == 3
    assert res == ["test4"]


def test_select_multiple_paginates_to_last_page_if_on_first_page_and_left_arrow_is_pressed():
    steps = iter([Keys.LEFT_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(
        options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8"],
        cursor_style="green",
        pagination=True,
        page_size=3,
    )

    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[ ] [green]test1[/green]\n\\[ ] test2\n\\[ ] test3[grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] [green]test7[/green]\n\\[ ] test8[grey58]\n\nPage 3/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]✓[/pink1]] [green]test7[/green]\n\\[ ] test8[grey58]\n\nPage 3/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]

    assert Live.update.call_count == 3
    assert res == ["test7"]


def test_select_multiple_paginates_to_first_page_if_on_last_page_and_right_arrow_is_pressed():
    steps = iter([Keys.RIGHT_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(
        options=["test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8"],
        cursor_style="green",
        pagination=True,
        page_size=3,
        cursor_index=6,
    )

    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[ ] [green]test7[/green]\n\\[ ] test8[grey58]\n\nPage 3/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[ ] [green]test1[/green]\n\\[ ] test2\n\\[ ] test3[grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]✓[/pink1]] [green]test1[/green]\n\\[ ] test2\n\\[ ] test3[grey58]\n\nPage 1/3[/grey58]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]

    assert Live.update.call_count == 3
    assert res == ["test1"]


def test_select_multiple_with_2_options_second_styled_starting_from_first_selecting_going_down_and_selecting_second():
    steps = iter([" ", Keys.DOWN_ARROW, " ", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "[yellow1]test2[/yellow1]"], tick_character="😋")
    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[  ] [pink1]test1[/pink1]\n\\[  ] [yellow1]test2[/yellow1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] [yellow1]test2[/yellow1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1][pink1]test2[/pink1][/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
        mock.call(
            renderable="\\[[pink1]😋[/pink1]] test1\n\\[[pink1]😋[/pink1]] [pink1][pink1]test2[/pink1][/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 4
    assert res == ["test1", "[yellow1]test2[/yellow1]"]


def test_select_multiple_ticks_correct_option():
    steps = iter([Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = select_multiple(options=["test1", "test2", "test3", "test4", "test5", "test6"], ticked_indices=[5], cursor_index=5)
    assert Live.update.call_args_list == [
        mock.call(
            renderable="\\[ ] test1\n\\[ ] test2\n\\[ ] test3\n\\[ ] test4\n\\[ ] test5\n\\[[pink1]✓[/pink1]] [pink1]test6[/pink1]\n\n([bold]space[/bold] to tick one, [bold]a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)"
        ),
    ]
    assert Live.update.call_count == 1
    assert res == ["test6"]
