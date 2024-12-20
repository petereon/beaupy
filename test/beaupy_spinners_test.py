from typing import Callable
from unittest.mock import MagicMock
import pytest

from beaupy.spinners import _spinners


def test_spinner_gets_created_as_expected():
    _spinners.Live = MagicMock()
    _spinners.Spinner(["t", "e", "s", "t"], "test", 10, False)

    _spinners.Live.assert_called_once()

    assert _spinners.Live.call_args[0] == ("",)
    assert _spinners.Live.call_args[1]["transient"] is False
    assert _spinners.Live.call_args[1]["refresh_per_second"] == 10

    assert isinstance(_spinners.Live.call_args[1]["get_renderable"], Callable)


def test_spinner_creation_fails_if_spinner_characters_are_an_empty_list():
    _spinners.Live = MagicMock()
    with pytest.raises(ValueError, match="`spinner_characters` can't be empty"):
        _spinners.Spinner([], "test", 10, False)


def test_spinner_callable_behaves_as_expected():
    _spinners.Live = MagicMock()
    _spinners.Spinner(["t", "e", "s", "t"], "test", 10, False)

    _spinners.Live.assert_called_once()

    get_renderable = _spinners.Live.call_args[1]["get_renderable"]

    assert get_renderable() == "t test"
    assert get_renderable() == "e test"
    assert get_renderable() == "s test"
    assert get_renderable() == "t test"


def test_spinner_start_methods_starts_a_live_display():
    _spinners.Live = MagicMock()
    result = _spinners.Spinner(["t", "e", "s", "t"], "test", 10, False)
    result.start()

    result._live_display.start.assert_called_once()


def test_spinner_stop_methods_stops_a_live_display():
    result = _spinners.Spinner(["t", "e", "s", "t"], "test", 10, False)
    result._live_display = MagicMock()
    result.stop()

    result._live_display.stop.assert_called_once()
