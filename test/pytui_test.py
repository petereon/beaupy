from unittest import mock
from ward import test, raises
from pytui import select, console
import readchar

@test('`select` with no options permissive')
def _():
    readchar.readkey = lambda: readchar.key.ENTER
    res = select(options = [])
    assert res == None
    
@test('`select` with no options strict')
def _():
    readchar.readkey = lambda: readchar.key.ENTER
    with raises(ValueError) as e:
        select(options = [], strict = True)
    
    assert str(e.raised) == '`options` cannot be empty'
    
        

@test('`select` with 1 option')
def _():
    steps = iter([readchar.key.ENTER])
    
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    select(options = ['test'])
    
    assert console.print.call_args_list[0] == mock.call('[pink1]> [/pink1]test')

    assert console.print.call_count == 1
    

@test('`select` with 1 option and down step')
def _():
    steps = iter([readchar.key.DOWN, readchar.key.ENTER])
    
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    select(options = ['test'])
    
    assert console.print.call_args_list[0] == mock.call('[pink1]> [/pink1]test')
    assert console.print.call_args_list[1] == mock.call('[pink1]> [/pink1]test')

    assert console.print.call_count == 2
    
    
@test('`select` with 4 options stepping down through all with random character inbetween and selecting last')
def _():
    steps = iter([readchar.key.DOWN,
                  readchar.key.DOWN,
                  "h",
                  readchar.key.DOWN,
                  readchar.key.ENTER])
    
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select(options = ['test1', 'test2', 'test3', 'test4'])
    
    assert console.print.call_args_list[0] == mock.call('[pink1]> [/pink1]test1\n  test2\n  test3\n  test4')
    assert console.print.call_args_list[1] == mock.call('  test1\n[pink1]> [/pink1]test2\n  test3\n  test4')
    assert console.print.call_args_list[2] == mock.call('  test1\n  test2\n[pink1]> [/pink1]test3\n  test4')
    assert console.print.call_args_list[3] == mock.call('  test1\n  test2\n[pink1]> [/pink1]test3\n  test4')
    assert console.print.call_args_list[4] == mock.call('  test1\n  test2\n  test3\n[pink1]> [/pink1]test4')
   
    assert console.print.call_count == 5
    assert res == 3
    
    
@test('`select` with 4 options stepping down through all and selecting last with `x` as a cursor and `green` as a cursor color')
def _():
    steps = iter([readchar.key.DOWN,
                  readchar.key.DOWN,
                  readchar.key.DOWN,
                  readchar.key.ENTER])
    
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select(options = ['test1', 'test2', 'test3', 'test4'], cursor='x ', cursor_color='green')
    
    assert console.print.call_args_list[0] == mock.call('[green]x [/green]test1\n  test2\n  test3\n  test4')
    assert console.print.call_args_list[1] == mock.call('  test1\n[green]x [/green]test2\n  test3\n  test4')
    assert console.print.call_args_list[2] == mock.call('  test1\n  test2\n[green]x [/green]test3\n  test4')
    assert console.print.call_args_list[3] == mock.call('  test1\n  test2\n  test3\n[green]x [/green]test4')
    assert console.print.call_count == 4
    assert res == 3