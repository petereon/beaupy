from unittest import mock

from beaupy import _beaupy as b
from yakh.key import Keys, Key
from ward import fixture, raises, test

from beaupy._beaupy import Config, Live, prompt
from beaupy._internals import ConversionError, ValidationError, Abort
import beaupy


def raise_keyboard_interrupt():
    raise KeyboardInterrupt()

@fixture
def set_raise_on_escape():
    Config.raise_on_escape = True
    yield
    Config.raise_on_escape = False


@test("Empty prompt with immediately pressing confirm")
def _():
    steps = iter([Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("")

    Live.update.assert_called_once_with(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])")
    assert res == ""


@test("Empty prompt typing `jozo` without validation and type and pressing confirm")
def _():
    steps = iter(["j", "o", "z", "o", Keys.ENTER])
    b.get_key = lambda: next(steps)
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


@test("Empty prompt typing `jozo` as secure input without validation and type and pressing confirm")
def _():
    steps = iter(["j", "o", "z", "o", Keys.ENTER])
    b.get_key = lambda: next(steps)
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


@test("Empty prompt typing `True` as secure input with bool as type")
def _():
    steps = iter(["T", "r", "u", "e", Keys.ENTER])
    b.get_key = lambda: next(steps)
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


@test("Empty prompt typing `12` as secure input with float as type")
def _():
    steps = iter(["1", "2", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("", secure=True, target_type=float)

    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
    ]
    assert isinstance(res, float)
    assert res == 12.0


@test("`Ask an actual question goddammit` as a prompt typing `No` and validating it is `No`")
def _():
    steps = iter(["o", Keys.LEFT_ARROW, Keys.LEFT_ARROW, "N", Keys.RIGHT_ARROW, Keys.RIGHT_ARROW, Keys.ENTER])
    b.get_key = lambda: next(steps)
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


@test("Empty prompt typing `12` as secure input with bool as type raising ConversionError")
def _():
    steps = iter(["1", "2", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    Config.raise_on_interrupt = True
    with raises(ConversionError):
        prompt("", secure=True, target_type=bool)
    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
    ]


@test("Empty prompt typing `12` as secure input with bool as type reporting a ConversionError")
def _():
    steps = iter(["1", "2", Keys.ENTER, Keys.ESC])
    b.get_key = lambda: next(steps)
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


@test("Empty prompt typing `12` as secure input validating that value is more than 20 and raising ValidationError")
def _():
    steps = iter(["1", "2", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    with raises(ValidationError):
        prompt("", secure=True, target_type=float, validator=lambda val: val > 20)
    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n(Confirm with [bold]enter[/bold])"),
    ]


@test("Empty prompt typing `12` as secure input validating that value is more than 20 and reporting ValidationError")
def _():
    steps = iter(["1", "2", Keys.ENTER, Keys.ESC])
    b.get_key = lambda: next(steps)
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

@test("Prompt with typing `J`, then deleting it and typing `No`")
def _():
    
    steps = iter(["J", Keys.BACKSPACE, Keys.BACKSPACE, "N", "o", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "No"


@test("Prompt with interrupt and raise on keyboard interrupt as False")
def _():
    Config.raise_on_interrupt = False
    Live.update = mock.MagicMock()
    b.get_key = lambda: Keys.CTRL_C
    ret = prompt(prompt="Try test")

    assert ret is None


@test("Prompt with interrupt and raise on keyboard interrupt as True")
def _():
    Config.raise_on_interrupt = True
    Live.update = mock.MagicMock()
    b.get_key = lambda: Keys.CTRL_C
    with raises(KeyboardInterrupt):
        prompt(prompt="Try test")


@test("Prompt with initial value without further input")
def _():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value="Hello, World!")
    assert res == "Hello, World!"


@test("Prompt with initial value and further input")
def _():
    steps = iter([*"World!", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value="Hello, ")
    assert res == "Hello, World!"


@test("Prompt with initial value and then backspace")
def _():
    steps = iter([Keys.BACKSPACE, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value="Hello,")
    assert res == "Hello"


@test("Prompt with empty initial value")
def _():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value="")
    assert res == ""


@test("Prompt with None initial value")
def _():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value=None)
    assert res == ""


@test("Prompt with None initial value and then backspace")
def _():
    steps = iter([Keys.BACKSPACE, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value=None)
    assert res == ""


@test("Prompt with typing `Hello`, pressing home, and then deleting one char")
def _():
    steps = iter([*"Hello", Keys.HOME, Keys.DELETE, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "ello"


@test("Prompt with typing `Hello`, pressing home, pressing end, and then backspacing one char")
def _():
    steps = iter([*"Hello", Keys.HOME, Keys.END, Keys.BACKSPACE, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "Hell"


@test("Prompt with typing `Hello`, pressing up and down, and making sure they don't change the result")
def _():
    steps = iter([*"Hello", Keys.UP_ARROW, Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "Hello"


@test("Verify that pressing delete on empty input doesn't fail")
def _():
    steps = iter([Keys.DELETE, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == ""


@test("Verify that pressing delete at the end of the input doesn't change anything")
def _():
    steps = iter([*"Hello", Keys.DELETE, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "Hello"


@test("Verify that home and end are working properly")
def _():
    steps = iter([*"ell", Keys.HOME, "H", Keys.END, "o", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "Hello"

@test("Verify that escape returns None")
def _():
    steps = iter([Keys.ESC])

    b.get_key = lambda: next(steps)
    res = prompt(prompt="Try test")
    assert res is None


@test("Verify that escape raises Abort when raise_on_escape is True")
def _(set_raise_on_escape=set_raise_on_escape):
    steps = iter([Key('esc', (27, ), is_printable=False)])

    b.get_key = lambda: next(steps)
    with raises(Abort) as e:
        prompt(prompt="Try test")
    assert str(e.raised) == "Aborted by user with key (27,)"
