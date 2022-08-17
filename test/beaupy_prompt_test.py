from ward import test, raises
from beaupy import prompt, console, ConversionError, ValidationError
import readchar
from unittest import mock

@test('Empty prompt with immediately pressing confirm')
def _():
    steps = iter([readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = prompt("")
    
    console.print.assert_called_once_with("\n> ")
    assert res == ''
    
@test('Empty prompt typing `jozo` without validation and type and pressing confirm')
def _():
    steps = iter(['j', 'o', 'z', 'o', readchar.key.ENTER]) 
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = prompt("")
    
    assert console.print.call_args_list[0] == mock.call("\n> ")
    assert console.print.call_args_list[1] == mock.call("\n> j")
    assert console.print.call_args_list[2] == mock.call("\n> jo")
    assert console.print.call_args_list[3] == mock.call("\n> joz")
    assert console.print.call_args_list[4] == mock.call("\n> jozo")
    assert res == 'jozo'
    
@test('Empty prompt typing `jozo` as secure input without validation and type and pressing confirm')
def _():
    steps = iter(['j', 'o', 'z', 'o', readchar.key.ENTER]) 
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = prompt("", secure=True)
    
    assert console.print.call_args_list[0] == mock.call("\n> ")
    assert console.print.call_args_list[1] == mock.call("\n> *")
    assert console.print.call_args_list[2] == mock.call("\n> **")
    assert console.print.call_args_list[3] == mock.call("\n> ***")
    assert console.print.call_args_list[4] == mock.call("\n> ****")
    assert res == 'jozo'
    
    
@test('Empty prompt typing `True` as secure input with bool as type')
def _():
    steps = iter(['T', 'r', 'u', 'e', readchar.key.ENTER]) 
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = prompt("", secure=True, target_type=bool)
    
    assert console.print.call_args_list[0] == mock.call("\n> ")
    assert console.print.call_args_list[1] == mock.call("\n> *")
    assert console.print.call_args_list[2] == mock.call("\n> **")
    assert console.print.call_args_list[3] == mock.call("\n> ***")
    assert console.print.call_args_list[4] == mock.call("\n> ****")
    assert res is True
    
@test('Empty prompt typing `12` as secure input with float as type')
def _():
    steps = iter(['1', '2', readchar.key.ENTER]) 
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = prompt("", secure=True, target_type=float)
    
    assert console.print.call_args_list[0] == mock.call("\n> ")
    assert console.print.call_args_list[1] == mock.call("\n> *")
    assert console.print.call_args_list[2] == mock.call("\n> **")
    assert isinstance(res, float)
    assert res == 12.0
    
@test('`Ask an actual question goddammit` as a prompt typing `No` and validating it is `No`')
def _():
    steps = iter(['N', 'o', readchar.key.ENTER]) 
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = prompt("Ask an actual question goddammit", validator=lambda val: val == 'No')
    
    assert console.print.call_args_list[0] == mock.call("Ask an actual question goddammit\n> ")
    assert console.print.call_args_list[1] == mock.call("Ask an actual question goddammit\n> N")
    assert console.print.call_args_list[2] == mock.call("Ask an actual question goddammit\n> No")
    assert isinstance(res, str)
    assert res == "No"
    
@test('Empty prompt typing `12` as secure input with bool as type raising ConversionError')
def _():
    steps = iter(['1', '2', readchar.key.ENTER]) 
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    
    with raises(ConversionError):
        prompt("", secure=True, target_type=bool)
        assert console.print.call_args_list[0] == mock.call("\n> ")
        assert console.print.call_args_list[1] == mock.call("\n> *")
        assert console.print.call_args_list[2] == mock.call("\n> **")
        

@test('Empty prompt typing `12` as secure input with bool as type raising ConversionError')
def _():
    steps = iter(['1', '2', readchar.key.ENTER]) 
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    
    with raises(ValidationError):
        prompt("", secure=True, target_type=float, validator=lambda val: val > 20)
        assert console.print.call_args_list[0] == mock.call("\n> ")
        assert console.print.call_args_list[1] == mock.call("\n> *")
        assert console.print.call_args_list[2] == mock.call("\n> **")