from unittest import mock

import pytest
from yakh.key import Key, Keys

from beaupy import _beaupy as b
from beaupy._beaupy import Config, Live, confirm, warnings
from beaupy._internals import Abort


def raise_keyboard_interrupt():
    raise KeyboardInterrupt()


def test_confirm_with_default_question():
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()
    res = confirm(question="Try test")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n  Yes\n[pink1]>[/pink1] No\n\n([bold]enter[/bold] to confirm)")
    ]
    assert Live.update.call_count == 1
    assert res is False


@mock.patch("beaupy._beaupy.get_key", side_effect=[Keys.ENTER])
def test_confirm_with_custom_yes_no_text(mock_get_key):
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", yes_text="No", no_text="Yes")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (N/Y) \n  No\n[pink1]>[/pink1] Yes\n\n([bold]enter[/bold] to confirm)")
    ]
    assert Live.update.call_count == 1
    assert res is False


def test_confirm_with_custom_yes_no_text_and_step_up():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", yes_text="No", no_text="Yes")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (N/Y) \n  No\n[pink1]>[/pink1] Yes\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (N/Y) No\n[pink1]>[/pink1] No\n  Yes\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res is True


def test_confirm_with_default_yes():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[pink1]>[/pink1] Yes\n  No\n\n([bold]enter[/bold] to confirm)")
    ]
    assert Live.update.call_count == 1
    assert res is True


def test_confirm_with_default_yes_and_step_down():
    steps = iter([Keys.DOWN_ARROW, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[pink1]>[/pink1] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[pink1]>[/pink1] No\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res is False


def test_confirm_with_default_yes_and_step_up():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[pink1]>[/pink1] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[pink1]>[/pink1] No\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res is False


def test_confirm_with_custom_cursor():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor="some long text")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[pink1]some long text[/pink1] Yes\n               No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) No\n               Yes\n[pink1]some long text[/pink1] No\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res is False


def test_confirm_with_custom_cursor_style():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_style="bold orange1")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[bold orange1]>[/bold orange1] No\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res is False


def test_confirm_with_typing_no():
    steps = iter(["n", "o", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_style="bold orange1")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) n\n  Yes\n[bold orange1]>[/bold orange1] No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) no\n  Yes\n[bold orange1]>[/bold orange1] No\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 3
    assert res is False


def test_confirm_with_case_sensitive_typing_no():
    steps = iter(["n", "o", Keys.ENTER, Keys.BACKSPACE, Keys.BACKSPACE, "N", "o", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_style="bold orange1", has_to_match_case=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) n\n  Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) no\n  Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) no\n  Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) n\n  Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) \n  Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) N\n  Yes\n[bold orange1]>[/bold orange1] No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[bold orange1]>[/bold orange1] No\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 8
    assert res is False


def test_confirm_with_no_char_prompt():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", char_prompt=False, cursor_style="bold orange1")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test: \n  Yes\n[bold orange1]>[/bold orange1] No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Try test: Yes\n[bold orange1]>[/bold orange1] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert Live.update.call_count == 2
    assert res is True


def test_confirm_with_enter_empty_confirms():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", cursor_style="bold orange1", default_is_yes=True, enter_empty_confirms=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n([bold]enter[/bold] to confirm)")
    ]
    assert Live.update.call_count == 1
    assert res is True


def test_confirm_with_empty_cursor_style():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    warnings.warn = mock.MagicMock()
    confirm(question="Test", cursor_style="")
    warnings.warn.assert_called_once_with("`cursor_style` should be a valid style, defaulting to `white`")


def test_confirm_with_keyboard_interrupt_and_raise_on_interrupt_false():
    Config.raise_on_interrupt = False
    b.get_key = lambda: Keys.CTRL_C
    res = confirm(question="Test", cursor_style="red")
    assert res is None


def test_confirm_with_keyboard_interrupt_and_raise_on_interrupt_true():
    Config.raise_on_interrupt = True
    b.get_key = lambda: Keys.CTRL_C
    with pytest.raises(KeyboardInterrupt):
        confirm(question="Test", cursor_style="red")


def test_confirm_with_typing_n_and_tab():
    steps = iter(["N", Keys.TAB, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Test (Y/N) N\n  Yes\n[red]>[/red] No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Test (Y/N) No\n  Yes\n[red]>[/red] No\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert ret is False


def test_confirm_with_typing_y():
    steps = iter(["Y", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Test (Y/N) Y\n[red]>[/red] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert ret is True


def test_confirm_with_backspace_on_empty():
    steps = iter([Keys.BACKSPACE, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert ret is True


def test_confirm_with_tab_on_empty():
    steps = iter([Keys.TAB, Keys.ENTER, Keys.ESC])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True, enter_empty_confirms=False)
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n  Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Test (Y/N) \n  Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Test (Y/N) \n  Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert ret is None


def test_confirm_returns_none_on_esc():
    steps = iter([Keys.ESC])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert ret is None


@pytest.fixture
def set_raise_on_escape():
    Config.raise_on_escape = True
    yield
    Config.raise_on_escape = False


def test_confirm_raises_abort_on_esc(set_raise_on_escape):
    steps = iter([Key("esc", (27,), is_printable=False)])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    with pytest.raises(Abort) as e:
        confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert str(e.value) == "Aborted by user with key (27,)"
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n([bold]enter[/bold] to confirm)"),
    ]
