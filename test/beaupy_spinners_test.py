from typing import Callable
from unittest.mock import MagicMock

import pytest

from beaupy.spinners import _spinners


def test_spinner_gets_created_as_expected():
    _spinners.Live = MagicMock()
    _spinners.Spinner(["t", "e", "s", "t"], text="test", refresh_per_second=10, transient=False)

    _spinners.Live.assert_called_once()

    assert _spinners.Live.call_args[0] == ("",)
    assert _spinners.Live.call_args[1]["transient"] is False
    assert _spinners.Live.call_args[1]["refresh_per_second"] == 10

    assert isinstance(_spinners.Live.call_args[1]["get_renderable"], Callable)


def test_spinner_creation_fails_if_spinner_characters_are_an_empty_list():
    _spinners.Live = MagicMock()
    with pytest.raises(ValueError, match="`spinner_characters` can't be empty"):
        _spinners.Spinner([], text="test", refresh_per_second=10, transient=False)


def test_spinner_callable_behaves_as_expected():
    _spinners.Live = MagicMock()
    _spinners.Spinner(["t", "e", "s", "t"], text="test", refresh_per_second=10, transient=False)

    _spinners.Live.assert_called_once()

    get_renderable = _spinners.Live.call_args[1]["get_renderable"]

    assert get_renderable() == "t test"
    assert get_renderable() == "e test"
    assert get_renderable() == "s test"
    assert get_renderable() == "t test"


def test_spinner_start_methods_starts_a_live_display():
    _spinners.Live = MagicMock()
    result = _spinners.Spinner(["t", "e", "s", "t"], text="test", refresh_per_second=10, transient=False)
    result.start()

    result._live_display.start.assert_called_once()


def test_spinner_stop_methods_stops_a_live_display():
    result = _spinners.Spinner(["t", "e", "s", "t"], text="test", refresh_per_second=10, transient=False)
    result._live_display = MagicMock()
    result.stop()

    result._live_display.stop.assert_called_once()


def test_spinner_text_and_options_are_keyword_only():
    with pytest.raises(TypeError):
        _spinners.Spinner(["t"], "test")


def test_spinner_passes_console_to_live_display():
    _spinners.Live = MagicMock()
    console = MagicMock()
    _spinners.Spinner(["t"], console=console)

    assert _spinners.Live.call_args[1]["console"] is console


def test_spinner_as_context_manager_starts_and_stops_it():
    _spinners.Live = MagicMock()
    spinner = _spinners.Spinner(["t"])

    with spinner as entered:
        assert entered is spinner
        spinner._live_display.start.assert_called_once()
        spinner._live_display.stop.assert_not_called()

    spinner._live_display.stop.assert_called_once()


def test_spinner_as_context_manager_stops_when_the_body_raises():
    _spinners.Live = MagicMock()
    spinner = _spinners.Spinner(["t"])

    with pytest.raises(RuntimeError), spinner:
        raise RuntimeError("boom")

    spinner._live_display.stop.assert_called_once()
