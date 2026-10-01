from unittest import mock

import pytest
from rich.console import Console
from yakh.key import Key, Keys

import beaupy
from beaupy import RemovedInV4Error
from beaupy import _beaupy as b
from beaupy._beaupy import (
    Config,
    KeyBindings,
    Live,
    confirm,
    prompt,
    select,
    select_multiple,
)


def test_accessing_removed_console_explains_migration():
    with pytest.raises(RemovedInV4Error, match=r"removed in beaupy 4\.0\.0.*Config\(console=my_console\)"):
        beaupy.console


def test_importing_removed_default_keys_explains_migration():
    with pytest.raises(RemovedInV4Error, match=r"removed in beaupy 4\.0\.0.*KeyBindings"):
        from beaupy import DefaultKeys  # noqa: F401


def test_assigning_removed_console_explains_migration():
    with pytest.raises(RemovedInV4Error, match=r"removed in beaupy 4\.0\.0"):
        b.console = Console()


def test_setting_config_on_class_explains_migration():
    with pytest.raises(AttributeError, match=r"removed in beaupy 4\.0\.0.*config=Config\(raise_on_escape=\.\.\.\)"):
        Config.raise_on_escape = True
    assert Config().raise_on_escape is False


def test_setting_keybindings_on_class_explains_migration():
    with pytest.raises(AttributeError, match=r"config=Config\(keys=KeyBindings\(up=\.\.\.\)\)"):
        KeyBindings.up = ["k"]


def test_unknown_module_attribute_still_raises_plain_attribute_error():
    with pytest.raises(AttributeError, match="has no attribute 'nope'"):
        beaupy.nope


@pytest.mark.parametrize(
    "call",
    [
        lambda: select(["a"], str),
        lambda: select_multiple(["a"], str),
        lambda: prompt("q", int),
        lambda: confirm("q", "Y"),
    ],
)
def test_only_first_argument_is_positional(call):
    with pytest.raises(TypeError):
        call()


def test_select_uses_console_from_config():
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()
    select(options=["a", "b", "c", "d", "e"], config=Config(console=Console(height=8)))

    # 8 rows: 2 for the page indicator, 2 for the instructions, leaving 4 options per page
    assert (
        Live.update.call_args.kwargs["renderable"]
        == "[pink1]>[/pink1] a\n  b\n  c\n  d[grey58]\n\nPage 1/2[/grey58]\n\n([bold]enter[/bold] to confirm)"
    )


def test_select_uses_keys_from_config():
    steps = iter(["j", Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()

    assert select(options=["a", "b"], config=Config(keys=KeyBindings(down=["j"]))) == "b"


def test_select_renders_title_and_custom_instructions():
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()
    select(options=["a"], title="Pick one", instructions="(enter = ok)")

    Live.update.assert_called_once_with(renderable="Pick one\n[pink1]>[/pink1] a\n\n(enter = ok)")


def test_select_multiple_renders_title_without_instructions():
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()
    select_multiple(options=["a"], title="Pick", instructions=None)

    Live.update.assert_called_once_with(renderable="Pick\n\\[ ] [pink1]a[/pink1]")


def test_prompt_and_confirm_render_custom_instructions():
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()
    prompt("q", instructions=None)
    confirm("q", instructions="(ok)")

    assert [c.kwargs["renderable"] for c in Live.update.call_args_list] == [
        "q\n> [black on white] [/black on white]",
        "q (Y/N) \n  Yes\n[pink1]>[/pink1] No\n\n(ok)",
    ]


def test_select_renders_sections_and_returns_sectioned_index():
    steps = iter([Keys.DOWN_ARROW, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    result = select(options={"Fruit": ["apple"], "Veg": ["leek", "kale"]}, cursor_index=("Veg", 0), return_index=True)

    assert result == ("Veg", 1)
    assert Live.update.call_args_list[0].kwargs["renderable"] == (
        "[bold]Fruit[/bold]\n  apple\n[bold]Veg[/bold]\n[pink1]>[/pink1] leek\n  kale\n\n([bold]enter[/bold] to confirm)"
    )


def test_select_repeats_section_header_at_top_of_page():
    steps = iter([Keys.RIGHT_ARROW, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    result = select(options={"Veg": ["leek", "kale", "okra"]}, page_size=2)

    assert result == "okra"
    assert Live.update.call_args.kwargs["renderable"] == (
        "[bold]Veg[/bold]\n[pink1]>[/pink1] okra[grey58]\n\nPage 2/2[/grey58]\n\n([bold]enter[/bold] to confirm)"
    )


def test_select_multiple_accepts_and_returns_sectioned_indices():
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()
    options = {"Fruit": ["apple"], "Veg": ["leek", "kale"]}

    assert select_multiple(options=options, ticked_indices=[("Veg", 1), ("Fruit", 0)], return_indices=True) == [("Veg", 1), ("Fruit", 0)]
    assert select_multiple(options=options, ticked_indices=[("Veg", 1)]) == ["kale"]


def test_select_with_all_empty_sections_raises_by_default():
    with pytest.raises(ValueError):
        select(options={"Empty": []})


def test_select_with_all_empty_sections_permissive():
    assert select(options={"Empty": []}, strict=False) is None


def typed(text):
    return [Key(c, (ord(c),), is_printable=True) for c in text]


def test_select_ignores_typing_by_default():
    steps = iter(typed("b") + [Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()

    assert select(options=["a", "b"]) == "a"


def test_select_filters_by_typed_text_and_shows_query():
    steps = iter(typed("AN") + [Keys.DOWN_ARROW, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    result = select(options=["apple", "[red]banana[/red]", "mango"], title="Fruit", filterable=True)

    assert result == "mango"
    assert Live.update.call_args.kwargs["renderable"] == (
        "Fruit [grey58]AN (2/3)[/grey58]\n  [red]banana[/red]\n[pink1]>[/pink1] mango\n\n([bold]enter[/bold] to confirm)"
    )


def test_select_filter_matches_markup_free_text_and_backspace_widens_it():
    steps = iter(typed("red") + [Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.END, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    renders = []
    Live.update.side_effect = lambda renderable: renders.append(renderable)

    assert select(options=["[red]apple[/red]", "kale"], filterable=True, instructions=None) == "kale"
    assert renders[3] == "[grey58]red (0/2)[/grey58]"


def test_select_ignores_confirm_when_nothing_matches():
    steps = iter(typed("zz") + [Keys.ENTER, Keys.BACKSPACE, Keys.BACKSPACE, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()

    assert select(options=["a", "b"], cursor_index=1, filterable=True) == "b"


def test_select_filter_handles_regex_characters_literally():
    steps = iter(typed("(") + [Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()

    assert select(options=["a", "b (c)"], filterable=True) == "b (c)"


def test_select_multiple_filter_keeps_hidden_ticks_and_select_all_ticks_visible_only():
    steps = iter(typed("e") + [Keys.CTRL_A, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()

    assert select_multiple(options=["apple", "kiwi", "pear", "fig"], ticked_indices=[1], filterable=True) == ["apple", "kiwi", "pear"]


def test_select_multiple_filter_accepts_a():
    steps = iter(typed("a") + [Keys.CTRL_A, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()

    assert select_multiple(options=["kiwi", "pear"], filterable=True) == ["pear"]


def test_select_multiple_select_all_toggles_all_options():
    steps = iter([Keys.CTRL_A, Keys.CTRL_A, Keys.CTRL_A, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()

    assert select_multiple(options=["a", "b", "c"], ticked_indices=[2]) == ["a", "b", "c"]


def test_select_multiple_select_all_respects_maximal_count_keeping_existing_ticks():
    steps = iter([Keys.CTRL_A, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()

    assert select_multiple(options=["a", "b", "c"], ticked_indices=[2], maximal_count=2) == ["a", "c"]


def test_select_multiple_a_no_longer_selects_all_by_default():
    steps = iter(typed("a") + [Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()

    assert select_multiple(options=["a", "b"]) == []


def test_default_console_does_not_highlight():
    assert Config().console.render_str("Option 42 is True").spans == []


@pytest.mark.parametrize(
    "call, error, message",
    [
        (lambda: select({"Veg": ["leek"]}, cursor_index=0), TypeError, r"must be a `\(section_name, index_in_section\)` tuple.*\('Veg', 0\)"),
        (lambda: select_multiple({"Veg": ["leek"]}, ticked_indices=[0]), TypeError, "must be a"),
        (lambda: select(["leek"], cursor_index=("Veg", 0)), TypeError, "but `options` is a list"),
        (lambda: select({"Veg": ["leek"]}, cursor_index=("Veg", 5)), ValueError, r"no option at \('Veg', 5\)"),
    ],
)
def test_index_kind_must_match_options_kind(call, error, message):
    with pytest.raises(error, match=message):
        call()


def test_sectioned_select_starts_on_first_option_by_default():
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()

    assert select({"Fruit": ["apple"], "Veg": ["leek"]}, return_index=True) == ("Fruit", 0)


def test_type_checker_ties_index_types_to_options_kind(tmp_path):
    mypy_api = pytest.importorskip("mypy.api")
    snippet = tmp_path / "snippet.py"
    snippet.write_text(
        """
from beaupy import select, select_multiple

flag: bool = True
reveal_type(select(["a"], return_index=True))
reveal_type(select({"s": ["a"]}, return_index=True))
reveal_type(select({"s": ["a"]}, return_index=flag))
reveal_type(select_multiple({"s": [1]}, return_indices=True))
select({"s": ["a"]}, cursor_index=0)
select(["a"], cursor_index=("s", 0))
select_multiple({"s": ["a"]}, ticked_indices=[0])
"""
    )
    stdout, _, _ = mypy_api.run(["--no-incremental", "--no-error-summary", "--hide-error-context", str(snippet)])
    lines = [line.split(": ", 1)[1] for line in stdout.splitlines() if "Possible overload" not in line and "note:     " not in line]

    assert lines == [
        'note: Revealed type is "int | None"',
        'note: Revealed type is "tuple[str, int] | None"',
        'note: Revealed type is "str | tuple[str, int] | None"',
        'note: Revealed type is "list[tuple[str, int]]"',
        'error: No overload variant of "select" matches argument types "dict[str, list[str]]", "int"  [call-overload]',
        'error: No overload variant of "select" matches argument types "list[str]", "tuple[str, int]"  [call-overload]',
        'error: List item 0 has incompatible type "int"; expected "tuple[str, int]"  [list-item]',
    ]


def test_select_raises_on_blank_option():
    with pytest.raises(ValueError, match=r"option at 1 is blank"):
        select(options=["a", "  ", "b"])


def test_select_raises_on_option_that_is_blank_once_markup_is_stripped():
    with pytest.raises(ValueError, match=r"option at 0 is blank"):
        select(options=["[red][/red]"])


def test_select_raises_on_blank_option_in_section():
    with pytest.raises(ValueError, match=r"option at \('Veg', 1\) is blank"):
        select(options={"Veg": ["leek", ""]})


def test_select_raises_on_blank_section_name():
    with pytest.raises(ValueError, match=r"section name '' is blank"):
        select(options={"": ["leek"]})


def test_select_multiple_raises_on_blank_option():
    with pytest.raises(ValueError, match=r"option at 0 is blank"):
        select_multiple(options=[""])


def test_select_multiple_filter_shows_match_count():
    steps = iter(typed("e") + [Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()

    select_multiple(options=["apple", "kiwi", "pear"], filterable=True)

    assert "(2/3)" in Live.update.call_args.kwargs["renderable"]


@pytest.mark.parametrize(
    "call",
    [
        lambda: select(["a"]),
        lambda: select_multiple(["a"]),
        lambda: prompt("q"),
        lambda: confirm("q"),
    ],
)
def test_ctrl_c_raises_keyboard_interrupt_by_default(call):
    b.get_key = lambda: Keys.CTRL_C
    Live.update = mock.MagicMock()

    with pytest.raises(KeyboardInterrupt):
        call()


class _FakeStdin:
    def __init__(self, tty):
        self._tty = tty

    def isatty(self):
        return self._tty


def _raise_terminal_error():
    raise OSError(25, "Inappropriate ioctl for device")


@pytest.mark.parametrize(
    "call",
    [
        lambda: select(["a"]),
        lambda: select_multiple(["a"]),
        lambda: prompt("q"),
        lambda: confirm("q"),
    ],
)
def test_reading_keys_without_a_terminal_raises_a_clear_error(call, monkeypatch):
    import sys

    monkeypatch.setattr(sys, "stdin", _FakeStdin(tty=False))
    b.get_key = _raise_terminal_error
    Live.update = mock.MagicMock()

    with pytest.raises(RuntimeError, match="Interactive terminal required") as e:
        call()
    assert isinstance(e.value.__cause__, OSError)


def test_key_reading_errors_with_a_terminal_are_not_masked(monkeypatch):
    import sys

    monkeypatch.setattr(sys, "stdin", _FakeStdin(tty=True))
    b.get_key = _raise_terminal_error
    Live.update = mock.MagicMock()

    with pytest.raises(OSError):
        select(["a"])


@pytest.mark.parametrize("kwargs", [{"yes_text": ""}, {"no_text": "   "}, {"yes_text": "[red][/red]"}])
def test_confirm_raises_on_blank_labels(kwargs):
    with pytest.raises(ValueError, match="is blank"):
        confirm("q", **kwargs)


def test_confirm_raises_when_labels_share_a_first_letter_and_hint_is_shown():
    with pytest.raises(ValueError, match=r"both start with 'Y'.*\(Y/y\)"):
        confirm("q", yes_text="Yes", no_text="yep")


def test_confirm_allows_shared_first_letter_without_hint_or_with_case_sensitivity():
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()

    assert confirm("q", yes_text="Yes", no_text="Yep", char_prompt=False, default_is_yes=True) is True
    assert confirm("q", yes_text="Yes", no_text="yep", has_to_match_case=True, default_is_yes=True) is True


def test_public_api_is_exactly_what_all_declares():
    assert all(hasattr(beaupy, name) for name in beaupy.__all__)
    assert not hasattr(beaupy, "sys")
    namespace = {}
    exec("from beaupy import *", namespace)
    assert sorted(n for n in namespace if n != "__builtins__") == sorted(beaupy.__all__)


def test_version_matches_the_installed_distribution():
    from importlib.metadata import version

    assert beaupy.__version__ == version("beaupy")


def test_type_checker_types_prompt_by_target_type(tmp_path):
    mypy_api = pytest.importorskip("mypy.api")
    snippet = tmp_path / "snippet.py"
    snippet.write_text(
        """
from beaupy import prompt

reveal_type(prompt("a"))
reveal_type(prompt("a", target_type=int))
prompt("a", target_type=int, validator=lambda s: s.startswith("x"))
"""
    )
    stdout, _, _ = mypy_api.run(["--no-incremental", "--no-error-summary", "--hide-error-context", str(snippet)])
    lines = [line.split(": ", 1)[1] for line in stdout.splitlines()]

    assert lines == [
        'note: Revealed type is "str | None"',
        'note: Revealed type is "int | None"',
        'error: "int" has no attribute "startswith"  [attr-defined]',
    ]


def test_options_can_be_any_sequence_or_mapping():
    from types import MappingProxyType

    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()

    assert select(("a", "b")) == "a"
    assert select(range(3), return_index=True) == 0
    assert select(MappingProxyType({"Veg": ("leek", "kale")}), cursor_index=("Veg", 1)) == "kale"


def test_type_checker_accepts_sequences_and_invariant_dict_variables(tmp_path):
    mypy_api = pytest.importorskip("mypy.api")
    snippet = tmp_path / "snippet.py"
    snippet.write_text(
        """
from typing import Dict, List, Tuple

from beaupy import select, select_multiple

sections: Dict[str, List[str]] = {"s": ["a"]}
names: Tuple[str, ...] = ("a", "b")
reveal_type(select(names))
reveal_type(select(sections, return_index=True))
reveal_type(select_multiple(names, ticked_indices=(0,)))
"""
    )
    stdout, _, _ = mypy_api.run(["--no-incremental", "--no-error-summary", "--hide-error-context", str(snippet)])

    assert [line.split(": ", 1)[1] for line in stdout.splitlines()] == [
        'note: Revealed type is "str | None"',
        'note: Revealed type is "tuple[str, int] | None"',
        'note: Revealed type is "list[str]"',
    ]


@pytest.mark.parametrize("fn", [select, select_multiple])
@pytest.mark.parametrize("options", ["abc", "", b"abc"])
def test_a_bare_string_is_rejected_as_options(fn, options):
    with pytest.raises(TypeError, match="not a bare (str|bytes)"):
        fn(options)


def test_validation_and_conversion_errors_are_value_errors():
    assert issubclass(beaupy.ValidationError, ValueError)
    assert issubclass(beaupy.ConversionError, ValueError)
    assert not issubclass(beaupy.ValidationError, beaupy.ConversionError)
    assert not issubclass(beaupy.ConversionError, beaupy.ValidationError)


def _prompt_with(text, **kwargs):
    steps = iter([*text, Keys.ENTER])
    b.get_key = lambda: next(steps)
    Live.update = mock.MagicMock()
    return prompt("q", **kwargs)


def test_a_failed_validator_is_a_validation_error_not_a_conversion_error():
    with pytest.raises(beaupy.ValidationError, match="Input `1` is invalid"):
        _prompt_with("1", target_type=int, validator=lambda n: n > 5)


def test_an_unconvertible_input_is_a_conversion_error():
    with pytest.raises(beaupy.ConversionError, match="cannot be converted to type"):
        _prompt_with("x", target_type=int)


def test_a_validator_that_itself_raises_value_error_is_not_swallowed_as_a_conversion_error():
    def validator(value):
        raise ValueError("my own complaint")

    with pytest.raises(ValueError, match="my own complaint") as e:
        _prompt_with("abc", validator=validator)
    assert not isinstance(e.value, beaupy.ConversionError)


@pytest.mark.parametrize("fn", [select, select_multiple])
def test_page_size_alone_paginates(fn):
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()

    fn(options=[f"opt{i}" for i in range(8)], page_size=3)

    rendered = Live.update.call_args.kwargs["renderable"]
    assert "Page 1/3" in rendered
    assert "opt2" in rendered and "opt3" not in rendered


@pytest.mark.parametrize("fn", [select, select_multiple])
def test_options_fitting_the_terminal_are_not_paginated_by_default(fn):
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()

    fn(options=["a", "b", "c"])

    assert "Page" not in Live.update.call_args.kwargs["renderable"]


@pytest.mark.parametrize("fn", [select, select_multiple])
def test_options_exceeding_the_terminal_are_paginated_by_default(fn):
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()

    fn(options=[str(i) for i in range(50)], config=Config(console=Console(height=20)))

    assert "Page 1/" in Live.update.call_args.kwargs["renderable"]


@pytest.mark.parametrize("fn", [select, select_multiple])
def test_the_pagination_flag_is_gone(fn):
    with pytest.raises(TypeError, match="pagination"):
        fn(options=["a"], pagination=True)


@pytest.mark.parametrize("cursor, width", [(">", 1), ("🌞", 2), ("⚔️", 2), ("✔️", 2), ("👍🏽", 2), ("🇨🇿", 2), ("漢", 2), ("dancing", 7)])
def test_unselected_rows_are_padded_to_the_cursor_width(cursor, width):
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()

    select(["one", "two"], cursor=cursor)

    unselected_row = Live.update.call_args.kwargs["renderable"].splitlines()[1]
    assert unselected_row == " " * (width + 1) + "two"


@pytest.mark.parametrize("tick, width", [("✓", 1), ("🎒", 2), ("❤️", 2), ("👨‍👩‍👧", 2)])
def test_unticked_boxes_are_as_wide_as_ticked_ones(tick, width):
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()

    select_multiple(["one", "two"], tick_character=tick, ticked_indices=[1])

    unticked, ticked = Live.update.call_args.kwargs["renderable"].splitlines()[:2]
    assert unticked.startswith("\\[" + " " * width + "]")
    assert ticked.startswith(f"\\[[pink1]{tick}[/pink1]]")


def _sectioned(count, sections):
    options = [f"opt{i}" for i in range(count)]
    if not sections:
        return options
    return {f"section{s}": options[s::sections] for s in range(sections)}


@pytest.mark.parametrize("fn", [select, select_multiple])
@pytest.mark.parametrize("height", [12, 20, 30])
@pytest.mark.parametrize("count, sections", [(3, 0), (50, 0), (50, 1), (50, 7), (50, 40), (9, 9)])
@pytest.mark.parametrize("title", ["", "Pick one\nor more"])
@pytest.mark.parametrize("filterable", [False, True])
def test_auto_page_size_never_renders_taller_than_the_terminal(fn, height, count, sections, title, filterable):
    keys = ([Keys.ENTER] if fn is select_multiple else []) + typed("o" if filterable else "") + [Keys.RIGHT_ARROW] * 2
    steps = iter([*keys, Keys.END, Keys.ESC])
    b.get_key = lambda: next(steps)
    renders = []
    Live.update = mock.MagicMock(side_effect=lambda renderable: renders.append(renderable))
    extra = {"minimal_count": 1} if fn is select_multiple else {}

    fn(_sectioned(count, sections), title=title, filterable=filterable, config=Config(console=Console(height=height)), **extra)

    tallest = max(len(r.splitlines()) for r in renders)
    assert tallest <= height, f"{tallest} lines rendered in a {height}-row terminal"


@pytest.mark.parametrize("fn", [select, select_multiple])
def test_auto_page_size_is_the_same_for_select_and_select_multiple(fn):
    b.get_key = lambda: Keys.ENTER
    Live.update = mock.MagicMock()
    # Both render the same chrome (page indicator + instructions), so both leave the same room for options
    fn([f"opt{i}" for i in range(50)], instructions="(done)", config=Config(console=Console(height=20)))

    assert Live.update.call_args.kwargs["renderable"].count("opt") == 20 - 4
