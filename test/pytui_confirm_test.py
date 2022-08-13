from unittest import mock
from ward import test, raises
from pytui import confirm, console
import readchar

@test("`confirm` with `Try test` as a question and defaults otherwise")
def _():
    readchar.readkey = lambda: readchar.key.ENTER
    console.print = mock.MagicMock()
    res = confirm(question="Try test")
    assert console.print.call_args_list[0] == mock.call("Try test (Y/N) \n  Yes\n[magenta1]> [/magenta1]No")
    assert console.print.call_count == 1
    assert res == False
    

@test("`confirm` with `Try test` as a question, `No` as a yes_text, `Yes` as a no_text and defaults otherwise")
def _():
    readchar.readkey = lambda: readchar.key.ENTER
    console.print = mock.MagicMock()
    res = confirm(question="Try test", yes_text="No", no_text="Yes")
    assert console.print.call_args_list[0] == mock.call("Try test (N/Y) \n  No\n[magenta1]> [/magenta1]Yes")
    assert console.print.call_count == 1
    assert res == False
    
@test("`confirm` with `Try test` as a question, `No` as a yes_text, `Yes` as a no_text and defaults otherwise, doing a step up to switch to yes")
def _():
    steps = iter([readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", yes_text="No", no_text="Yes")
    assert console.print.call_args_list[0] == mock.call("Try test (N/Y) \n  No\n[magenta1]> [/magenta1]Yes")
    assert console.print.call_args_list[1] == mock.call('Try test (N/Y) No\n[magenta1]> [/magenta1]No\n  Yes')
    assert console.print.call_count == 2
    assert res == True
    
@test("`confirm` with `Try test` as a question and yes as a default")
def _():
    steps = iter([readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert console.print.call_args_list[0] == mock.call("Try test (Y/N) \n[magenta1]> [/magenta1]Yes\n  No")
    assert console.print.call_count == 1
    assert res == True
    
@test("`confirm` with `Try test` as a question and yes as a default, going down to select no")
def _():
    steps = iter([readchar.key.DOWN, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert console.print.call_args_list[0] == mock.call("Try test (Y/N) \n[magenta1]> [/magenta1]Yes\n  No")
    assert console.print.call_args_list[1] == mock.call("Try test (Y/N) No\n  Yes\n[magenta1]> [/magenta1]No")
    assert console.print.call_count == 2
    assert res == False
    
@test("`confirm` with `Try test` as a question and yes as a default going up to select no")
def _():
    steps = iter([readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True)
    assert console.print.call_args_list[0] == mock.call("Try test (Y/N) \n[magenta1]> [/magenta1]Yes\n  No")
    assert console.print.call_args_list[1] == mock.call("Try test (Y/N) No\n  Yes\n[magenta1]> [/magenta1]No")
    assert console.print.call_count == 2
    assert res == False
    
@test("`confirm` with `Try test` as a question and yes as a default going up to select no with `some long text ` as a cursor")
def _():
    steps = iter([readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor="some long text ")
    assert console.print.call_args_list[0] == mock.call("Try test (Y/N) \n[magenta1]some long text [/magenta1]Yes\n               No")
    assert console.print.call_args_list[1] == mock.call("Try test (Y/N) No\n               Yes\n[magenta1]some long text [/magenta1]No")
    assert console.print.call_count == 2
    assert res == False
    
    
@test("`confirm` with `Try test` as a question and yes as a default going up to select no with `bold orange1` as a cursor color")
def _():
    steps = iter([readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = confirm(question="Try test", default_is_yes=True, cursor_color='bold orange1')
    assert console.print.call_args_list[0] == mock.call("Try test (Y/N) \n[bold orange1]> [/bold orange1]Yes\n  No")
    assert console.print.call_args_list[1] == mock.call("Try test (Y/N) No\n  Yes\n[bold orange1]> [/bold orange1]No")
    assert console.print.call_count == 2
    assert res == False

# TODO: include tests for the rest of parameters `has_to_match_case`, `enter_empty_confirms` and `char_prompt`