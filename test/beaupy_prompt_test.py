from unittest import mock

import pytest
from yakh.key import Key, Keys

from beaupy import _beaupy as b
from beaupy._beaupy import Config, Live, prompt
from beaupy._internals import Abort, ConversionError, ValidationError


def raise_keyboard_interrupt():
    raise KeyboardInterrupt()


@pytest.fixture
def set_raise_on_escape():
    Config.raise_on_escape = True
    yield
    Config.raise_on_escape = False


def test_empty_prompt_with_immediately_pressing_confirm():
    steps = iter([Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("")

    Live.update.assert_called_once_with(renderable="\n> [black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)")
    assert res == ""


def test_empty_prompt_typing_jozo_without_validation_and_type_and_pressing_confirm():
    steps = iter(["j", "o", "z", "o", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("")

    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> j[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> jo[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> joz[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> jozo[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert res == "jozo"


def test_empty_prompt_typing_jozo_as_secure_input_without_validation_and_type_and_pressing_confirm():
    steps = iter(["j", "o", "z", "o", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("", secure=True)

    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> ***[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> ****[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert res == "jozo"


def test_empty_prompt_typing_true_as_secure_input_with_bool_as_type():
    steps = iter(["T", "r", "u", "e", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("", secure=True, target_type=bool)

    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> ***[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> ****[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert res is True


def test_empty_prompt_typing_12_as_secure_input_with_float_as_type():
    steps = iter(["1", "2", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("", secure=True, target_type=float)

    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert isinstance(res, float)
    assert res == 12.0


def test_ask_an_actual_question_goddammit_as_a_prompt_typing_no_and_validating_it_is_no():
    steps = iter(["o", Keys.LEFT_ARROW, Keys.LEFT_ARROW, "N", Keys.RIGHT_ARROW, Keys.RIGHT_ARROW, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt("Ask an actual question goddammit", validator=lambda val: val == "No")

    assert Live.update.call_args_list == [
        mock.call(renderable="Ask an actual question goddammit\n> [black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Ask an actual question goddammit\n> o[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Ask an actual question goddammit\n> [black on white]o[/black on white] \n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Ask an actual question goddammit\n> [black on white]o[/black on white] \n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Ask an actual question goddammit\n> N[black on white]o[/black on white] \n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Ask an actual question goddammit\n> No[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="Ask an actual question goddammit\n> No[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
    ]
    assert isinstance(res, str)
    assert res == "No"


def test_empty_prompt_typing_12_as_secure_input_with_bool_as_type_raising_conversionerror():
    steps = iter(["1", "2", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    Config.raise_on_interrupt = True
    with pytest.raises(ConversionError):
        prompt("", secure=True, target_type=bool)
    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
    ]


def test_empty_prompt_typing_12_as_secure_input_with_bool_as_type_reporting_a_conversionerror():
    steps = iter(["1", "2", Keys.ENTER, Keys.ESC])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    Config.raise_on_interrupt = False
    prompt("", secure=True, target_type=bool, raise_type_conversion_fail=False)
    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(
            renderable="\n> **[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)\n[red]Error:[/red] Input <secure_input> cannot be converted to type `<class 'bool'>`"
        ),
    ]


def test_empty_prompt_typing_12_as_secure_input_validating_that_value_is_more_than_20_and_raising_validationerror():
    steps = iter(["1", "2", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    with pytest.raises(ValidationError):
        prompt("", secure=True, target_type=float, validator=lambda val: val > 20)
    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
    ]


def test_empty_prompt_typing_12_as_secure_input_validating_that_value_is_more_than_20_and_reporting_validationerror():
    steps = iter(["1", "2", Keys.ENTER, Keys.ESC])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    Config.raise_on_interrupt = False
    prompt("", secure=True, target_type=float, validator=lambda val: val > 20, raise_validation_fail=False)
    assert Live.update.call_args_list == [
        mock.call(renderable="\n> [black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> *[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(renderable="\n> **[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)"),
        mock.call(
            renderable="\n> **[black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)\n[red]Error:[/red] Input <secure_input> is invalid"
        ),
    ]


def test_prompt_with_typing_j_then_deleting_it_and_typing_no():
    steps = iter(["J", Keys.BACKSPACE, Keys.BACKSPACE, "N", "o", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "No"


def test_prompt_with_interrupt_and_raise_on_keyboard_interrupt_as_false():
    Config.raise_on_interrupt = False
    Live.update = mock.MagicMock()
    b.get_key = lambda: Keys.CTRL_C
    ret = prompt(prompt="Try test")

    assert ret is None


def test_prompt_with_interrupt_and_raise_on_keyboard_interrupt_as_true():
    Config.raise_on_interrupt = True
    Live.update = mock.MagicMock()
    b.get_key = lambda: Keys.CTRL_C
    with pytest.raises(KeyboardInterrupt):
        prompt(prompt="Try test")


def test_prompt_with_initial_value_without_further_input():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value="Hello, World!")
    assert res == "Hello, World!"


def test_prompt_with_initial_value_and_further_input():
    steps = iter([*"World!", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value="Hello, ")
    assert res == "Hello, World!"


def test_prompt_with_initial_value_and_then_backspace():
    steps = iter([Keys.BACKSPACE, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value="Hello,")
    assert res == "Hello"


def test_prompt_with_empty_initial_value():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value="")
    assert res == ""


def test_prompt_with_none_initial_value():
    steps = iter([Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value=None)
    assert res == ""


def test_prompt_with_none_initial_value_and_then_backspace():
    steps = iter([Keys.BACKSPACE, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test", initial_value=None)
    assert res == ""


def test_prompt_with_typing_hello_pressing_home_and_then_deleting_one_char():
    steps = iter([*"Hello", Keys.HOME, Keys.DELETE, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "ello"


def test_prompt_with_typing_hello_pressing_home_pressing_end_and_then_backspacing_one_char():
    steps = iter([*"Hello", Keys.HOME, Keys.END, Keys.BACKSPACE, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "Hell"


def test_prompt_with_typing_hello_pressing_up_and_down_and_making_sure_they_dont_change_the_result():
    steps = iter([*"Hello", Keys.UP_ARROW, Keys.DOWN_ARROW, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "Hello"


def test_verify_that_pressing_delete_on_empty_input_doesnt_fail():
    steps = iter([Keys.DELETE, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == ""


def test_verify_that_pressing_delete_at_the_end_of_the_input_doesnt_change_anything():
    steps = iter([*"Hello", Keys.DELETE, Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "Hello"


def test_verify_that_home_and_end_are_working_properly():
    steps = iter([*"ell", Keys.HOME, "H", Keys.END, "o", Keys.ENTER])

    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    res = prompt(prompt="Try test")
    assert res == "Hello"


def test_verify_that_escape_returns_none():
    steps = iter([Keys.ESC])

    b.get_key = lambda: next(steps)
    res = prompt(prompt="Try test")
    assert res is None


def test_verify_that_escape_raises_abort_when_raise_on_escape_is_true(set_raise_on_escape):
    steps = iter([Key("esc", (27,), is_printable=False)])

    b.get_key = lambda: next(steps)
    with pytest.raises(Abort) as e:
        prompt(prompt="Try test")
    assert str(e.value) == "Aborted by user with key (27,)"


def test_verify_that_completion_works():
    steps = iter([Keys.TAB, Keys.TAB, Keys.ENTER])

    b.get_key = lambda: next(steps)
    res = prompt(prompt="Try test", completion=lambda _: ["Hello", "World"])
    assert res == "World"


def test_verify_that_completion_renders_properly():
    steps = iter([Keys.TAB, Keys.TAB, Keys.TAB, Keys.ENTER])

    Live.update = mock.MagicMock()
    b.get_key = lambda: next(steps)
    res = prompt(prompt="Try test", completion=lambda _: ["Hello", "World"])

    assert Live.update.call_args_list == [
        mock.call(renderable='Try test\n> [black on white] [/black on white]\n\n([bold]enter[/bold] to confirm)'),
        mock.call(
            renderable='Try test\n> Hello[black on white] [/black on white]\n[black on white]Hello[/black on white] World\n\n([bold]enter[/bold] to confirm)'
        ),
        mock.call(
            renderable='Try test\n> World[black on white] [/black on white]\nHello [black on white]World[/black on white]\n\n([bold]enter[/bold] to confirm)'
        ),
        mock.call(
            renderable='Try test\n> Hello[black on white] [/black on white]\n[black on white]Hello[/black on white] World\n\n([bold]enter[/bold] to confirm)'
        ),
    ]

    assert res == "Hello"
