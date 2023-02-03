from unittest import mock

from beaupy import _beaupy as b
from ward import fixture, raises, test

from beaupy._beaupy import Config, Live, confirm, warnings
from beaupy._internals import Abort

from yakh.key import Keys, Key


def raise_keyboard_interrupt():
    raise KeyboardInterrupt()


@test("`confirm` with `Try test` as a question and defaults otherwise")
def _():
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()
    res = confirm(question="Try test")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n  Yes\n[pink1]>[/pink1] No\n\n(Confirm with [bold]enter[/bold])")
    ]
    assert Live.update.call_count == 1
    assert res == False


@test("`confirm` with `Try test` as a question, `No` as a yes_text, `Yes` as a no_text and defaults otherwise")
@mock.patch('beaupy._beaupy.get_key', side_effect=[Keys.ENTER])
def _():
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", yes_text="No", no_text="Yes")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (N/Y) \n  No\n[pink1]>[/pink1] Yes\n\n(Confirm with [bold]enter[/bold])")
    ]
    assert Live.update.call_count == 1
    assert res == False


@test(
    "`confirm` with `Try test` as a question, `No` as a yes_text, `Yes` as a no_text and defaults otherwise, doing a step up to switch to yes",
)
def _():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", yes_text="No", no_text="Yes")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (N/Y) \n  No\n[pink1]>[/pink1] Yes\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (N/Y) No\n[pink1]>[/pink1] No\n  Yes\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == True


@test("`confirm` with `Try test` as a question and yes as a default")
def _():
    steps = iter([Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[pink1]>[/pink1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])")
    ]
    assert Live.update.call_count == 1
    assert res == True


@test("`confirm` with `Try test` as a question and yes as a default, going down to select no")
def _():
    steps = iter([Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[pink1]>[/pink1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[pink1]>[/pink1] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == False


@test("`confirm` with `Try test` as a question and yes as a default going up to select no")
def _():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[pink1]>[/pink1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[pink1]>[/pink1] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `some long text ` as a cursor",
)
def _():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor="some long text")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[pink1]some long text[/pink1] Yes\n               No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(
            renderable="Try test (Y/N) No\n               Yes\n[pink1]some long text[/pink1] No\n\n(Confirm with [bold]enter[/bold])"
        ),
    ]
    assert Live.update.call_count == 2
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color",
)
def _():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_style="bold orange1")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color",
)
def _():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_style="bold orange1")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color, typing the `no` answer",
)
def _():
    steps = iter(["n", "o", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_style="bold orange1")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) n\n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) no\n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 3
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color, case sensitive typing the `no` answer",
)
def _():
    steps = iter(
        [
            "n",
            "o",
            Keys.ENTER,
            Keys.BACKSPACE,
            Keys.BACKSPACE,
            "N",
            "o",
            Keys.ENTER,
        ]
    )

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(
        question="Try test",
        default_is_yes=True,
        cursor_style="bold orange1",
        has_to_match_case=True,
    )
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) n\n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) no\n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) no\n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) n\n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) \n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) N\n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test (Y/N) No\n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 8
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color and no char prompt",
)
def _():
    steps = iter([Keys.UP_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", char_prompt=False, cursor_style="bold orange1")
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test: \n  Yes\n[bold orange1]>[/bold orange1] No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Try test: Yes\n[bold orange1]>[/bold orange1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert Live.update.call_count == 2
    assert res == True


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color and enter empty confirms",)
def _():
    steps = iter([Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = confirm(question="Try test", cursor_style="bold orange1", default_is_yes=True, enter_empty_confirms=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No\n\n(Confirm with [bold]enter[/bold])")
    ]
    assert Live.update.call_count == 1
    assert res == True


@test("`confirm` with `Test` as a question and empty cursor style")
def _():
    steps = iter([Keys.ENTER])

    b.get_key = lambda: next(steps)
    warnings.warn = mock.MagicMock()
    confirm(question="Test", cursor_style="")

    warnings.warn.assert_called_once_with("`cursor_style` should be a valid style, defaulting to `white`")


@test("`confirm` with `Test` as a question with KeyboardInterrupt and raise_on_interrupt as False")
def _():
    Config.raise_on_interrupt = False
    b.get_key = lambda: Keys.CTRL_C
    res = confirm(question="Test", cursor_style="red")

    assert res == None


@test("`confirm` with `Test` as a question with KeyboardInterrupt and raise_on_interrupt as True")
def _():
    Config.raise_on_interrupt = True
    b.get_key = lambda: Keys.CTRL_C
    with raises(KeyboardInterrupt):
        confirm(question="Test", cursor_style="red")


@test("`confirm` with `Test` as a question, typing `N` and pressing `\\t`")
def _():
    steps = iter(["N", Keys.TAB, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Test (Y/N) N\n  Yes\n[red]>[/red] No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Test (Y/N) No\n  Yes\n[red]>[/red] No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert ret is False


@test("`confirm` with `Test` as a question, typing `Y`")
def _():
    steps = iter(["Y", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Test (Y/N) Y\n[red]>[/red] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert ret is True

@test("`confirm` with `Test` as a question, and pressing Backspace on empty")
def _():
    steps = iter([Keys.BACKSPACE, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert ret is True

@test("`confirm` with `Test` as a question, and pressing Tab on empty")
def _():
    steps = iter([Keys.TAB, Keys.ENTER, Keys.ESC])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True, enter_empty_confirms=False)
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Test (Y/N) \n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="Test (Y/N) \n  Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
    ]

    assert ret is None


@test("`confirm` returns None when ESC is pressed")
def _():
    steps = iter([Keys.ESC])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert ret is None

@fixture
def set_raise_on_escape():
    Config.raise_on_escape = True
    yield
    Config.raise_on_escape = False
    

@test("`confirm` raises Abort when ESC is pressed and raise_on_abort is True")
def _(set_raise_on_escape=set_raise_on_escape):
    steps = iter([Key('esc', (27, ), is_printable=False)])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    with raises(Abort) as e:
        confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert str(e.raised) == "Aborted by user with key (27,)"
    assert Live.update.call_args_list == [
        mock.call(renderable="Test (Y/N) \n[red]>[/red] Yes\n  No\n\n(Confirm with [bold]enter[/bold])"),
    ]