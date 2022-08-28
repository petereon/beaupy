from unittest import mock
from ward import test, raises
from beaupy import select_multiple, console, Config, logging
import readchar


@test("`select_multiple` with no options permissive")
def _():
    readchar.readkey = lambda: readchar.key.ENTER
    res = select_multiple(options=[])
    assert res == []


@test("`select_multiple` with no options strict")
def _():
    readchar.readkey = lambda: readchar.key.ENTER
    with raises(ValueError) as e:
        select_multiple(options=[], strict=True)

    assert str(e.raised) == "`options` cannot be empty"


@test("`select_multiple` with 2 options starting from first selecting going down and selecting second also")
def _():
    steps = iter([readchar.key.SPACE, readchar.key.DOWN, readchar.key.SPACE, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋")
    assert console.print.call_args_list == [
        mock.call("\\[  ] [pink1]test1[/pink1]\n\\[  ] test2"),
        mock.call("\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] test2"),
        mock.call("\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]"),
        mock.call("\\[[pink1]😋[/pink1]] test1\n\\[[pink1]😋[/pink1]] [pink1]test2[/pink1]"),
    ]
    assert console.print.call_count == 4
    assert res == ["test1", "test2"]
    

@test("`select_multiple` with 2 options starting from first selecting going down and selecting second also with return_indices as True")
def _():
    steps = iter([readchar.key.SPACE, readchar.key.DOWN, readchar.key.SPACE, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋", return_indices=True)
    assert console.print.call_args_list == [
        mock.call("\\[  ] [pink1]test1[/pink1]\n\\[  ] test2"),
        mock.call("\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] test2"),
        mock.call("\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]"),
        mock.call("\\[[pink1]😋[/pink1]] test1\n\\[[pink1]😋[/pink1]] [pink1]test2[/pink1]"),
    ]
    assert console.print.call_count == 4
    assert res == [0, 1]


@test("`select_multiple` with 2 options `✓` as tick character and yellow1 as color starting from second selecting and going up")
def _():
    steps = iter([readchar.key.SPACE, readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select_multiple(
        options=["test1", "test2"],
        tick_character="✓",
        tick_style="yellow1",
        cursor_index=1,
    )
    assert console.print.call_args_list == [
        mock.call("\\[ ] test1\n\\[ ] [pink1]test2[/pink1]"),
        mock.call("\\[ ] test1\n\\[[yellow1]✓[/yellow1]] [pink1]test2[/pink1]"),
        mock.call("\\[ ] [pink1]test1[/pink1]\n\\[[yellow1]✓[/yellow1]] test2"),
    ]
    assert console.print.call_count == 3
    assert res == ["test2"]


@test(
    "`select_multiple` with 2 options `✓` as tick character and yellow1 as color starting from second selecting and going up with 1st option preselected"
)
def _():
    steps = iter([readchar.key.SPACE, readchar.key.UP, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select_multiple(
        options=["test1", "test2"],
        tick_character="✓",
        tick_style="yellow1",
        cursor_index=1,
        ticked_indices=[0],
    )
    assert console.print.call_args_list == [
        mock.call("\\[[yellow1]✓[/yellow1]] test1\n\\[ ] [pink1]test2[/pink1]"),
        mock.call("\\[[yellow1]✓[/yellow1]] test1\n\\[[yellow1]✓[/yellow1]] [pink1]test2[/pink1]"),
        mock.call("\\[[yellow1]✓[/yellow1]] [pink1]test1[/pink1]\n\\[[yellow1]✓[/yellow1]] test2"),
    ]
    assert console.print.call_count == 3
    assert res == ["test1", "test2"]


@test("`select_multiple` with 2 options starting from first selecting going down and selecting second also with `maximal_count` of 1")
def _():
    steps = iter([readchar.key.SPACE, readchar.key.DOWN, readchar.key.SPACE, readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋", maximal_count=1)

    assert console.print.call_args_list == [
        mock.call("\\[  ] [pink1]test1[/pink1]\n\\[  ] test2"),
        mock.call("\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] test2"),
        mock.call("\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]"),
        mock.call('Must select at most 1 options'),
        mock.call("\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]"),
    ]
    assert console.print.call_count == 5
    assert res == ["test1"]


@test("`select_multiple` with 2 options starting from first selecting going down and selecting second also with `minimal_count` of 2")
def _():
    steps = iter(
        [
            readchar.key.SPACE,
            readchar.key.DOWN,
            readchar.key.ENTER,
            readchar.key.SPACE,
            readchar.key.ENTER,
        ]
    )

    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋", minimal_count=2)
    assert console.print.call_args_list == [
        mock.call("\\[  ] [pink1]test1[/pink1]\n\\[  ] test2"),
        mock.call("\\[[pink1]😋[/pink1]] [pink1]test1[/pink1]\n\\[  ] test2"),
        mock.call("\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]"),
        mock.call("Must select at least 2 options"),
        mock.call("\\[[pink1]😋[/pink1]] test1\n\\[  ] [pink1]test2[/pink1]"),
        mock.call("\\[[pink1]😋[/pink1]] test1\n\\[[pink1]😋[/pink1]] [pink1]test2[/pink1]"),
    ]
    assert console.print.call_count == 6
    assert res == ["test1", "test2"]


@test("`select_multiple` with 2 options and calling `Ctrl+C` with raise on keyboard interrupt False")
def _():
    steps = iter([readchar.key.CTRL_C])
    Config.raise_on_interrupt = False
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    res = select_multiple(options=["test1", "test2"], tick_character="😋")
    assert console.print.call_args_list == [mock.call("\\[  ] [pink1]test1[/pink1]\n\\[  ] test2")]
    assert console.print.call_count == 1
    assert res == []


@test("`select_multiple` with 2 options and calling `Ctrl+C` with raise on keyboard interrupt True")
def _():
    steps = iter([readchar.key.CTRL_C])
    Config.raise_on_interrupt = True
    readchar.readkey = lambda: next(steps)
    console.print = mock.MagicMock()
    with raises(KeyboardInterrupt):
        select_multiple(options=["test1", "test2"], tick_character="😋")


@test("`select_multiple` with 2 options and invalid tick style")
def _():
    steps = iter([readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    logging.warning = mock.MagicMock()
    select_multiple(options=["test1", "test2"], tick_style="")
    logging.warning.assert_called_once_with("`tick_style` should be a valid style, defaulting to `white`")


@test("`select_multiple` with 2 options and invalid cursor style")
def _():
    steps = iter([readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    logging.warning = mock.MagicMock()
    select_multiple(options=["test1", "test2"], cursor_style="")
    logging.warning.assert_called_once_with("`cursor_style` should be a valid style, defaulting to `white`")
