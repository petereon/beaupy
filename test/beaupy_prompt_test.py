from unittest import mock

import readchar
from ward import raises, test

from beaupy._beaupy import Config, ConversionError, Live, ValidationError, prompt


@test("Empty prompt with immediately pressing confirm", tags=["v1", "prompt"])
def _():
    steps = iter([readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("")

    Live.update.assert_called_once_with(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])")
    assert res == ""


@test("Empty prompt typing `jozo` without validation and type and pressing confirm", tags=["v1", "prompt"])
def _():
    steps = iter(["j", "o", "z", "o", readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("")

    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> j[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> jo[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> joz[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> jozo[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert res == "jozo"


@test("Empty prompt typing `jozo` as secure input without validation and type and pressing confirm", tags=["v1", "prompt"])
def _():
    steps = iter(["j", "o", "z", "o", readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("", secure=True)

    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> ***[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> ****[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert res == "jozo"


@test("Empty prompt typing `True` as secure input with bool as type", tags=["v1", "prompt"])
def _():
    steps = iter(["T", "r", "u", "e", readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("", secure=True, target_type=bool)

    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> ***[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> ****[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert res is True


@test("Empty prompt typing `12` as secure input with float as type", tags=["v1", "prompt"])
def _():
    steps = iter(["1", "2", readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("", secure=True, target_type=float)

    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert isinstance(res, float)
    assert res == 12.0


@test("`Ask an actual question goddammit` as a prompt typing `No` and validating it is `No`", tags=["v1", "prompt"])
def _():
    steps = iter(["o", readchar.key.LEFT, readchar.key.LEFT, "N", readchar.key.RIGHT, readchar.key.RIGHT, readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("Ask an actual question goddammit", validator=lambda val: val == "No")

    assert Live.update.call_args_list == [
        mock.call(renderable="Ask an actual question goddammit\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(
            renderable="Ask an actual question goddammit\n> o[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"
        ),
        mock.call(
            renderable="Ask an actual question goddammit\n> [black on white]o[/black on white] \n\n(Confirm with [bold]enter[/bold])"
        ),
        mock.call(
            renderable="Ask an actual question goddammit\n> [black on white]o[/black on white] \n\n(Confirm with [bold]enter[/bold])"
        ),
        mock.call(
            renderable="Ask an actual question goddammit\n> N[black on white]o[/black on white] \n\n(Confirm with [bold]enter[/bold])"
        ),
        mock.call(
            renderable="Ask an actual question goddammit\n> No[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"
        ),
        mock.call(
            renderable="Ask an actual question goddammit\n> No[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"
        ),
    ]
    assert isinstance(res, str)
    assert res == "No"


@test("Empty prompt typing `12` as secure input with bool as type raising ConversionError", tags=["v1", "prompt"])
def _():
    steps = iter(["1", "2", readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    Config.raise_on_interrupt = True
    with raises(ConversionError):
        prompt("", secure=True, target_type=bool)
    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
    ]


@test("Empty prompt typing `12` as secure input with bool as type reporting a ConversionError", tags=["v1", "prompt"])
def _():
    steps = iter(["1", "2", readchar.key.ENTER, readchar.key.CTRL_C])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    Config.raise_on_interrupt = False
    prompt("", secure=True, target_type=bool, raise_type_conversion_fail=False)
    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(
            renderable="\n> **[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])\n[red]Error:[/red] Input <secure_input> cannot be converted to type `<class 'bool'>`"
        ),
    ]


@test("Empty prompt typing `12` as secure input validating that value is more than 20 and raising ValidationError", tags=["v1", "prompt"])
def _():
    steps = iter(["1", "2", readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    with raises(ValidationError):
        prompt("", secure=True, target_type=float, validator=lambda val: val > 20)
    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
    ]


@test("Empty prompt typing `12` as secure input validating that value is more than 20 and reporting ValidationError", tags=["v1", "prompt"])
def _():
    steps = iter(["1", "2", readchar.key.ENTER, readchar.key.CTRL_C])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    Config.raise_on_interrupt = False
    prompt("", secure=True, target_type=float, validator=lambda val: val > 20, raise_validation_fail=False)
    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(
            renderable="\n> **[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])\n[red]Error:[/red] Input <secure_input> is invalid"
        ),
    ]


@test("Prompt with typing `J`, then deleting it and typing `No`", tags=["v1", "prompt"])
def _():
    steps = iter(["J", readchar.key.BACKSPACE, readchar.key.BACKSPACE, "N", "o", readchar.key.ENTER])

    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "No"


@test("Prompt with interrupt and raise on keyboard iterrupt as False", tags=["v1", "prompt"])
def _():
    steps = iter([readchar.key.CTRL_C])
    Config.raise_on_interrupt = False
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    ret = prompt(prompt="Try test")

    assert ret is None


@test("Prompt with interrupt and raise on keyboard iterrupt as True", tags=["v1", "prompt"])
def _():
    steps = iter([readchar.key.CTRL_C])
    Config.raise_on_interrupt = True
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()

    with raises(KeyboardInterrupt):
        prompt(prompt="Try test")


@test("Prompt with initial value without further input", tags=["v1", "prompt"])
def _():
    steps = iter([readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value="Hello, World!")
    assert res == "Hello, World!"


@test("Prompt with initial value and further input", tags=["v1", "prompt"])
def _():
    steps = iter([*"World!", readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value="Hello, ")
    assert res == "Hello, World!"


@test("Prompt with initial value and then backspace", tags=["v1", "prompt"])
def _():
    steps = iter([readchar.key.BACKSPACE, readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value="Hello,")
    assert res == "Hello"


@test("Prompt with empty initial value", tags=["v1", "prompt"])
def _():
    steps = iter([readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value="")
    assert res == ""


@test("Prompt with None initial value", tags=["v1", "prompt"])
def _():
    steps = iter([readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value=None)
    assert res == ""


@test("Prompt with None initial value and then backspace", tags=["v1", "prompt"])
def _():
    steps = iter([readchar.key.BACKSPACE, readchar.key.ENTER])
    readchar.readkey = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value=None)
    assert res == ""
