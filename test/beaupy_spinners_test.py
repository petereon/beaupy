from typing import Callable
from unittest.mock import MagicMock

from ward import raises, test

from beaupy.spinners import _spinners


@test("Spinner gets created as expected")
def _():
    _spinners.Live = MagicMock()
    _spinners.Spinner(["t", "e", "s", "t"], "test", 10, False)

    _spinners.Live.assert_called_once()

    assert _spinners.Live.call_args[0] == ("",)
    assert _spinners.Live.call_args[1]["transient"] == False
    assert _spinners.Live.call_args[1]["refresh_per_second"] == 10

    assert isinstance(_spinners.Live.call_args[1]["get_renderable"], Callable)


@test("Spinner creation fails if `spinner_characters` are an empty list")
def _():
    _spinners.Live = MagicMock()
    with raises(ValueError) as e:
        _spinners.Spinner([], "test", 10, False)

    assert str(e.raised) == "`spinner_characters` can't be empty"


@test("Spinner callable behaves as expected")
def _():
    _spinners.Live = MagicMock()
    _spinners.Spinner(["t", "e", "s", "t"], "test", 10, False)

    _spinners.Live.assert_called_once()

    get_renderable = _spinners.Live.call_args[1]["get_renderable"]

    assert get_renderable() == "t test"
    assert get_renderable() == "e test"
    assert get_renderable() == "s test"
    assert get_renderable() == "t test"


@test("Spinner `start` methods starts a live display")
def _():
    _spinners.Live = MagicMock()
    result = _spinners.Spinner(["t", "e", "s", "t"], "test", 10, False)
    result.start()

    result._live_display.start.assert_called_once()


@test("Spinner `stop` methods stops a live display")
def _():
    result = _spinners.Spinner(["t", "e", "s", "t"], "test", 10, False)
    result._live_display = MagicMock()
    result.stop()

    result._live_display.stop.assert_called_once()
