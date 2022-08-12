from unittest import mock
from ward import test, raises
from pytui import select, console
import readchar

from pytui.pytui import select_multiple

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
    
    
@test('`select` with 4 options starting from second going up and selecting first with `x` as a cursor and `green` as a cursor color')
def _():
    steps = iter([readchar.key.UP,
                  readchar.key.ENTER])
    
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select(options = ['test1', 'test2', 'test3', 'test4'], cursor='x ', cursor_color='green', cursor_index=1)
    
    assert console.print.call_args_list[0] == mock.call('  test1\n[green]x [/green]test2\n  test3\n  test4')
    assert console.print.call_args_list[1] == mock.call('[green]x [/green]test1\n  test2\n  test3\n  test4')
    assert console.print.call_count == 2
    assert res == 0
    

@test('`select_multiple` with no options permissive')
def _():
    readchar.readkey = lambda: readchar.key.ENTER
    res = select_multiple(options = [])
    assert res == []
    
@test('`select_multiple` with no options strict')
def _():
    readchar.readkey = lambda: readchar.key.ENTER
    with raises(ValueError) as e:
        select_multiple(options = [], strict = True)
    
    assert str(e.raised) == '`options` cannot be empty'
    
    
@test('`select_multiple` with 2 options starting from first selecting going down and selecting second also')
def _():
    steps = iter([readchar.key.SPACE,
                  readchar.key.DOWN,
                  readchar.key.SPACE,
                  readchar.key.ENTER])
    
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select_multiple(options = ['test1', 'test2'], tick_character='😋')
    assert console.print.call_args_list[0] == mock.call('\\[ ] [pink1]test1[/pink1]\n\\[ ] test2')
    assert console.print.call_args_list[1] == mock.call('\\[[cyan1]😋[/cyan1]] [pink1]test1[/pink1]\n\\[ ] test2')
    assert console.print.call_args_list[2] == mock.call('\\[[cyan1]😋[/cyan1]] test1\n\\[ ] [pink1]test2[/pink1]')
    assert console.print.call_args_list[3] == mock.call('\\[[cyan1]😋[/cyan1]] test1\n\\[[cyan1]😋[/cyan1]] [pink1]test2[/pink1]')
    assert console.print.call_count == 4
    assert res == [0,1]
    
@test('`select_multiple` with 2 options `✓` as tick character and yellow1 as color starting from second selecting and going up')
def _():
    steps = iter([readchar.key.SPACE,
                  readchar.key.UP,
                  readchar.key.ENTER])
    
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select_multiple(options = ['test1', 'test2'], tick_character='✓', tick_color='yellow1', cursor_index=1)
    assert console.print.call_args_list[0] == mock.call('\\[ ] test1\n\\[ ] [pink1]test2[/pink1]')
    assert console.print.call_args_list[1] == mock.call('\\[ ] test1\n\\[[yellow1]✓[/yellow1]] [pink1]test2[/pink1]')
    assert console.print.call_args_list[2] == mock.call('\\[ ] [pink1]test1[/pink1]\n\\[[yellow1]✓[/yellow1]] test2')
    assert console.print.call_count == 3
    assert res == [1]
    
@test('`select_multiple` with 2 options `✓` as tick character and yellow1 as color starting from second selecting and going up with 1st option preselected')
def _():
    steps = iter([readchar.key.SPACE,
                  readchar.key.UP,
                  readchar.key.ENTER])
    
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select_multiple(options = ['test1', 'test2'], tick_character='✓', tick_color='yellow1', cursor_index=1, ticked_indices=[0])
    assert console.print.call_args_list[0] == mock.call('\\[[yellow1]✓[/yellow1]] test1\n\\[ ] [pink1]test2[/pink1]')
    assert console.print.call_args_list[1] == mock.call('\\[[yellow1]✓[/yellow1]] test1\n\\[[yellow1]✓[/yellow1]] [pink1]test2[/pink1]')
    assert console.print.call_args_list[2] == mock.call('\\[[yellow1]✓[/yellow1]] [pink1]test1[/pink1]\n\\[[yellow1]✓[/yellow1]] test2')
    assert console.print.call_count == 3
    assert res == [0,1]
    
    
@test('`select_multiple` with 2 options starting from first selecting going down and selecting second also with `maximal_count` of 1')
def _():
    steps = iter([readchar.key.SPACE,
                  readchar.key.DOWN,
                  readchar.key.SPACE,
                  readchar.key.ENTER])
    
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select_multiple(options = ['test1', 'test2'], tick_character='😋', maximal_count=1)
    assert console.print.call_args_list[0] == mock.call('\\[ ] [pink1]test1[/pink1]\n\\[ ] test2')
    assert console.print.call_args_list[1] == mock.call('\\[[cyan1]😋[/cyan1]] [pink1]test1[/pink1]\n\\[ ] test2')
    assert console.print.call_args_list[2] == mock.call('\\[[cyan1]😋[/cyan1]] test1\n\\[ ] [pink1]test2[/pink1]')
    assert console.print.call_args_list[3] == mock.call('\\[[cyan1]😋[/cyan1]] test1\n\\[ ] [pink1]test2[/pink1]')
    assert console.print.call_count == 4
    assert res == [0]


@test('`select_multiple` with 2 options starting from first selecting going down and selecting second also with `minimal_count` of 2')
def _():
    steps = iter([readchar.key.SPACE,
                  readchar.key.DOWN,
                  readchar.key.ENTER,
                  readchar.key.SPACE,
                  readchar.key.ENTER,])
    
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select_multiple(options = ['test1', 'test2'], tick_character='😋', minimal_count=2)
    print(console.print.call_args_list[5])
    assert console.print.call_args_list[0] == mock.call('\\[ ] [pink1]test1[/pink1]\n\\[ ] test2')
    assert console.print.call_args_list[1] == mock.call('\\[[cyan1]😋[/cyan1]] [pink1]test1[/pink1]\n\\[ ] test2')
    assert console.print.call_args_list[2] == mock.call('\\[[cyan1]😋[/cyan1]] test1\n\\[ ] [pink1]test2[/pink1]')
    assert console.print.call_args_list[3] == mock.call('Must select at least 2 options')
    assert console.print.call_args_list[4] == mock.call('\\[[cyan1]😋[/cyan1]] test1\n\\[ ] [pink1]test2[/pink1]')
    assert console.print.call_args_list[5] == mock.call('\\[[cyan1]😋[/cyan1]] test1\n\\[[cyan1]😋[/cyan1]] [pink1]test2[/pink1]')
    assert console.print.call_count == 6
    assert res == [0,1]


# TODO: Include tests for `confirm`
# TODO: Drive implementation of `prompt` by the tests