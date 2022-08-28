from unittest import mock
from ward import test, raises
from beaupy import confirm, console, logging, Config
import readchar


@test("`confirm` with `Try test` as a question and defaults otherwise")
def _():
    readchar.readkey = lambda: readchar.key.ENTER
    console.print = mock.MagicMock()
    res = confirm(question="Try test")
    assert console.print.call_args_list == [mock.call("Try test (Y/N) \n  Yes\n[pink1]>[/pink1] No")]
    assert console.print.call_count == 1
    assert res == False


@test("`confirm` with `Try test` as a question, `No` as a yes_text, `Yes` as a no_text and defaults otherwise")
def _():
    readchar.readkey = lambda: readchar.key.ENTER
    console.print = mock.MagicMock()
    res = confirm(question="Try test", yes_text="No", no_text="Yes")
    assert console.print.call_args_list == [mock.call("Try test (N/Y) \n  No\n[pink1]>[/pink1] Yes")]
    assert console.print.call_count == 1
    assert res == False


@test(
    "`confirm` with `Try test` as a question, `No` as a yes_text, `Yes` as a no_text and defaults otherwise, doing a step up to switch to yes"
)
def _():
    steps = iter([readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", yes_text="No", no_text="Yes")
    assert console.print.call_args_list == [
        mock.call("Try test (N/Y) \n  No\n[pink1]>[/pink1] Yes"),
        mock.call("Try test (N/Y) No\n[pink1]>[/pink1] No\n  Yes"),
    ]
    assert console.print.call_count == 2
    assert res == True


@test("`confirm` with `Try test` as a question and yes as a default")
def _():
    steps = iter([readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert console.print.call_args_list == [mock.call("Try test (Y/N) \n[pink1]>[/pink1] Yes\n  No")]
    assert console.print.call_count == 1
    assert res == True


@test("`confirm` with `Try test` as a question and yes as a default, going down to select no")
def _():
    steps = iter([readchar.key.DOWN, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert console.print.call_args_list == [
        mock.call("Try test (Y/N) \n[pink1]>[/pink1] Yes\n  No"),
        mock.call("Try test (Y/N) No\n  Yes\n[pink1]>[/pink1] No"),
    ]
    assert console.print.call_count == 2
    assert res == False


@test("`confirm` with `Try test` as a question and yes as a default going up to select no")
def _():
    steps = iter([readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert console.print.call_args_list == [
        mock.call("Try test (Y/N) \n[pink1]>[/pink1] Yes\n  No"),
        mock.call("Try test (Y/N) No\n  Yes\n[pink1]>[/pink1] No"),
    ]
    assert console.print.call_count == 2
    assert res == False


@test("`confirm` with `Try test` as a question and yes as a default going up to select no with `some long text ` as a cursor")
def _():
    steps = iter([readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor="some long text")
    assert console.print.call_args_list == [
        mock.call("Try test (Y/N) \n[pink1]some long text[/pink1] Yes\n               No"),
        mock.call("Try test (Y/N) No\n               Yes\n[pink1]some long text[/pink1] No"),
    ]
    assert console.print.call_count == 2
    assert res == False


@test("`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color")
def _():
    steps = iter([readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_style="bold orange1")
    assert console.print.call_args_list == [
        mock.call("Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No"),
        mock.call("Try test (Y/N) No\n  Yes\n[bold orange1]>[/bold orange1] No"),
    ]
    assert console.print.call_count == 2
    assert res == False


@test("`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color")
def _():
    steps = iter([readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_style="bold orange1")
    assert console.print.call_args_list == [
        mock.call("Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No"),
        mock.call("Try test (Y/N) No\n  Yes\n[bold orange1]>[/bold orange1] No"),
    ]
    assert console.print.call_count == 2
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color, typing the `no` answer"
)
def _():
    steps = iter(["n", "o", readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_style="bold orange1")
    assert console.print.call_args_list == [
        mock.call("Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No"),
        mock.call("Try test (Y/N) n\n  Yes\n[bold orange1]>[/bold orange1] No"),
        mock.call("Try test (Y/N) no\n  Yes\n[bold orange1]>[/bold orange1] No"),
    ]
    assert console.print.call_count == 3
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color, case sensitive typing the `no` answer"
)
def _():
    steps = iter(
        [
            "n",
            "o",
            readchar.key.ENTER,
            readchar.key.BACKSPACE,
            readchar.key.BACKSPACE,
            "N",
            "o",
            readchar.key.ENTER,
        ]
    )

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(
        question="Try test",
        default_is_yes=True,
        cursor_style="bold orange1",
        has_to_match_case=True,
    )
    assert console.print.call_args_list == [
        mock.call("Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No"),
        mock.call("Try test (Y/N) n\n  Yes\n  No"),
        mock.call("Try test (Y/N) no\n  Yes\n  No"),
        mock.call("Try test (Y/N) no\n  Yes\n  No"),
        mock.call("Try test (Y/N) n\n  Yes\n  No"),
        mock.call("Try test (Y/N) \n  Yes\n  No"),
        mock.call("Try test (Y/N) N\n  Yes\n[bold orange1]>[/bold orange1] No"),
        mock.call("Try test (Y/N) No\n  Yes\n[bold orange1]>[/bold orange1] No"),
    ]
    assert console.print.call_count == 8
    assert res == False


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color and no char prompt"
)
def _():
    steps = iter([readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", char_prompt=False, cursor_style="bold orange1")
    assert console.print.call_args_list == [
        mock.call("Try test: \n  Yes\n[bold orange1]>[/bold orange1] No"),
        mock.call("Try test: Yes\n[bold orange1]>[/bold orange1] Yes\n  No"),
    ]
    assert console.print.call_count == 2
    assert res == True


@test(
    "`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color and enter empty confirms"
)
def _():
    steps = iter([readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", cursor_style="bold orange1", default_is_yes=True, enter_empty_confirms=True)
    assert console.print.call_args_list == [mock.call("Try test (Y/N) \n[bold orange1]>[/bold orange1] Yes\n  No")]
    assert console.print.call_count == 1
    assert res == True


@test("`confirm` with `Test` as a question and empty cursor style")
def _():
    steps = iter([readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    logging.warning = mock.MagicMock()
    confirm(question="Test", cursor_style="")

    logging.warning.assert_called_once_with("`cursor_style` should be a valid style, defaulting to `white`")


@test("`confirm` with `Test` as a question with KeyboardInterrupt and raise_on_interrupt as False")
def _():
    steps = iter([readchar.key.CTRL_C])
    Config.raise_on_interrupt = False
    readchar.readkey = lambda: next(steps)
    res = confirm(question="Test", cursor_style="red")

    assert res == None


@test("`confirm` with `Test` as a question with KeyboardInterrupt and raise_on_interrupt as True")
def _():
    steps = iter([readchar.key.CTRL_C])
    Config.raise_on_interrupt = True
    readchar.readkey = lambda: next(steps)

    with raises(KeyboardInterrupt):
        confirm(question="Test", cursor_style="red")


@test("`confirm` with `Test` as a question, typing `N` and pressing `\\t`")
def _():
    steps = iter(["N", "\t", readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert console.print.call_args_list == [
        mock.call("Test (Y/N) \n[red]>[/red] Yes\n  No"),
        mock.call("Test (Y/N) N\n  Yes\n[red]>[/red] No"),
        mock.call("Test (Y/N) No\n  Yes\n[red]>[/red] No"),
    ]
    assert ret is False
    

@test("`confirm` with `Test` as a question, typing `Y`")
def _():
    steps = iter(["Y", readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    ret = confirm(question="Test", cursor_style="red", default_is_yes=True)
    assert console.print.call_args_list == [
        mock.call("Test (Y/N) \n[red]>[/red] Yes\n  No"),
        mock.call("Test (Y/N) Y\n[red]>[/red] Yes\n  No"),
    ]
    
    assert ret is True
