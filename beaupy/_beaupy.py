#! /usr/bin/env python3
"""
A Python library of interactive CLI elements you have been looking for
"""

__license__ = 'MIT'

import math
import sys
import warnings
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Callable, Dict, List, Literal, Optional, Sequence, Tuple, Type, TypeVar, Union, overload

from questo import prompt as qprompt
from questo import select as qselect
from rich.console import Console
from rich.live import Live
from yakh import get_key
from yakh.key import Key, Keys

from beaupy._internals import (
    Abort,
    ConversionError,
    SectionedPosition,
    TargetType,
    ValidationError,
    _cursor_hidden,
    _flatten_options,
    _InstanceOnly,
    _option_labels,
    _paginate_back,
    _paginate_forward,
    _prompt_key_handler,
    _RemovedGlobalsModule,
    _render_prompt,
    _render_select,
    _render_select_multiple,
    _to_flat_index,
    _update_rendered,
    _validate_prompt_value,
    _visible_indexes,
)

sys.modules[__name__].__class__ = _RemovedGlobalsModule

KeyList = List[Union[Tuple[int, ...], str]]


def _keys(*keys: Union[Tuple[int, ...], str]) -> Any:
    return field(default_factory=lambda: list(keys))


@dataclass
class KeyBindings(metaclass=_InstanceOnly):
    """Keybindings used by the elements. Pass an instance via `Config(keys=KeyBindings(...))`.

    Attributes:
        escape(List[Union[Tuple[int, ...], str]]): Keys that escape the current context.
        select(List[Union[Tuple[int, ...], str]]): Keys that trigger list element selection.
        confirm(List[Union[Tuple[int, ...], str]]): Keys that trigger list confirmation.
        backspace(List[Union[Tuple[int, ...], str]]): Keys that trigger deletion of the previous character.
        delete(List[Union[Tuple[int, ...], str]]): Keys that trigger deletion of the next character.
        down(List[Union[Tuple[int, ...], str]]): Keys that select the element below.
        up(List[Union[Tuple[int, ...], str]]): Keys that select the element above.
        left(List[Union[Tuple[int, ...], str]]): Keys that select the element to the left.
        right(List[Union[Tuple[int, ...], str]]): Keys that select the element to the right.
        tab(List[Union[Tuple[int, ...], str]]): Keys that complete the current selection in `confirm`.
        home(List[Union[Tuple[int, ...], str]]): Keys that move to the beginning of the context.
        end(List[Union[Tuple[int, ...], str]]): Keys that move to the end of the context.
        interrupt(List[Union[Tuple[int, ...], str]]): Keys that interrupt the current context.
        select_all(List[Union[Tuple[int, ...], str]]): Keys that tick/untick all options in `select_multiple`.
    """

    escape: KeyList = _keys(Keys.ESC)
    select: KeyList = _keys(' ')
    confirm: KeyList = _keys(Keys.ENTER)
    backspace: KeyList = _keys(Keys.BACKSPACE)
    delete: KeyList = _keys(Keys.DELETE)
    down: KeyList = _keys(Keys.DOWN_ARROW, Keys.NUMPAD_DOWN_ARROW)
    up: KeyList = _keys(Keys.UP_ARROW, Keys.NUMPAD_UP_ARROW)
    left: KeyList = _keys(Keys.LEFT_ARROW, Keys.NUMPAD_LEFT_ARROW)
    right: KeyList = _keys(Keys.RIGHT_ARROW, Keys.NUMPAD_RIGHT_ARROW)
    tab: KeyList = _keys(Keys.TAB)
    home: KeyList = _keys(Keys.HOME)
    end: KeyList = _keys(Keys.END)
    interrupt: KeyList = _keys(Keys.CTRL_C)
    select_all: KeyList = _keys(Keys.CTRL_A)

    def is_navigation(self, keypress: Key) -> bool:
        return any(keypress in keys for keys in (self.up, self.down, self.right, self.left, self.home, self.end))


@dataclass
class Config(metaclass=_InstanceOnly):
    """Configuration of the elements. Create an instance and pass it via the `config=` argument.

    Attributes:
        raise_on_interrupt(bool): If True, functions will raise KeyboardInterrupt whenever one is encountered when waiting for input,
        otherwise, they will return some sane alternative to their usual return. For `select`, `prompt` and `confirm` this means `None`,
        while for `select_multiple` it means an empty list - `[]`. Defaults to False.
        raise_on_escape(bool): If True, functions will raise Abort whenever the escape key is encountered when waiting for input, otherwise,
        they will return some sane alternative to their usual return. For `select`, `prompt` and `confirm` this means `None`, while for
        `select_multiple` it means an empty list - `[]`.  Defaults to False.
        transient(bool): If False, elements will remain displayed after their context has ended. Defaults to True.
        console(rich.console.Console): Console the elements are rendered to. Pass your own to share it with other Rich
        output, e.g. a `rich.live.Live`. Defaults to `Console(stderr=True, highlight=False)`.
        keys(KeyBindings): Keybindings used by the elements. Defaults to `KeyBindings()`.
    """

    raise_on_interrupt: bool = False
    raise_on_escape: bool = False
    transient: bool = True
    console: Console = field(default_factory=lambda: Console(stderr=True, highlight=False))
    keys: KeyBindings = field(default_factory=KeyBindings)


KeyBindings._locked = True
Config._locked = True

_CONFIRM_INSTRUCTIONS = '([bold]enter[/bold] to confirm)'
_SELECT_MULTIPLE_INSTRUCTIONS = '([bold]space[/bold] to tick one, [bold]ctrl+a[/bold] to tick/untick all, [bold]enter[/bold] to confirm)'


def _navigate_select(state: qselect.SelectState, keypress: Key, keys: KeyBindings, visible: List[int]) -> qselect.SelectState:
    """Moves the cursor among `visible` option indexes (all options unless filtered)."""
    if not visible:
        return state
    total_options = len(visible)
    position = visible.index(state.index) if state.index in visible else 0

    page: int = position // state.page_size + 1
    total_pages = math.ceil(total_options / state.page_size)

    show_from = (page - 1) * state.page_size
    show_to = min(show_from + state.page_size, total_options)

    if keypress in keys.up:
        if position <= show_from and state.pagination:
            page = _paginate_back(page, total_pages)
        position = (position - 1) % total_options
    elif keypress in keys.down:
        if position > show_to - 2 and state.pagination:
            page = _paginate_forward(page, total_pages)
        position = (position + 1) % total_options
    elif keypress in keys.right and state.pagination:
        page = _paginate_forward(page, total_pages)
        position = (page - 1) * state.page_size
    elif keypress in keys.left and state.pagination:
        page = _paginate_back(page, total_pages)
        position = (page - 1) * state.page_size
    elif keypress in keys.home:
        position = 0
    elif keypress in keys.end:
        position = total_options - 1

    state.index = visible[position]
    return state


def _update_filter(state: qselect.SelectState, keypress: Key, keys: KeyBindings, labels: List[str]) -> bool:
    """Edits the filter query for typed/backspace keys. Returns False if the key isn't a filter key."""
    if keypress in keys.backspace:
        state.filter = state.filter[:-1]
    elif getattr(keypress, 'is_printable', False):
        state.filter += keypress.key
    else:
        return False
    visible = _visible_indexes(state, labels)
    if visible and state.index not in visible:
        state.index = visible[0]
    return True


def _navigate_select_multiple(
    state: qselect.SelectState,
    keypress: Key,
    minimal_count: int,
    maximal_count: Union[int, None],
    config: Config,
    labels: Optional[List[str]] = None,
) -> qselect.SelectState:
    """Handles a keypress. `labels` enables filtering by typing when given."""
    keys = config.keys
    visible = _visible_indexes(state, labels or [])
    if keypress in keys.interrupt:
        state.selected_indexes = []
        if config.raise_on_interrupt:
            raise KeyboardInterrupt()
        state.abort = True

    elif keys.is_navigation(keypress):
        state = _navigate_select(state, keypress=keypress, keys=keys, visible=visible)
    elif keypress in keys.select_all:
        targets = visible[:maximal_count] if maximal_count is not None else visible
        if all(i in state.selected_indexes for i in targets):
            state.selected_indexes = [i for i in state.selected_indexes if i not in targets]
        else:
            ticked = state.selected_indexes + [i for i in targets if i not in state.selected_indexes]
            if maximal_count is not None:
                ticked = ticked[:maximal_count]
                state.error = f'Must select at most {maximal_count} options'
            state.selected_indexes = sorted(ticked)
    elif keypress in keys.select and state.index in visible:
        if state.index in state.selected_indexes:
            state.selected_indexes.remove(state.index)
        else:
            if maximal_count is not None and len(state.selected_indexes) + 1 > maximal_count:
                state.error = f'Must select at most {maximal_count} options'
            else:
                state.selected_indexes.append(state.index)
    elif keypress in keys.confirm:
        if minimal_count > len(state.selected_indexes):
            state.error = f'Must select at least {minimal_count} options'
        else:
            state.exit = True
    elif keypress in keys.escape:
        state.selected_indexes = []
        if config.raise_on_escape:
            raise Abort(keypress)
        state.exit = True
    elif labels is not None:
        _update_filter(state, keypress, keys, labels)
    return state


def prompt(
    prompt: str,
    *,
    target_type: Type[TargetType] = str,
    validator: Callable[[TargetType], bool] = lambda input: True,
    secure: bool = False,
    raise_validation_fail: bool = True,
    raise_type_conversion_fail: bool = True,
    initial_value: Optional[str] = None,
    completion: Optional[Callable[[str], List[str]]] = None,
    instructions: Optional[str] = _CONFIRM_INSTRUCTIONS,
    config: Optional[Config] = None,
) -> TargetType:
    """Function that prompts the user for written input

    Args:
        prompt (str): The prompt that will be displayed
        target_type (Union[Type[T], Type[str]], optional): Type to convert the answer to. Defaults to str.
        validator (Callable[[Any], bool], optional): Optional function to validate the input. Defaults to lambda input: True.
        secure (bool, optional): If True, input will be hidden. Defaults to False.
        raise_validation_fail (bool, optional): If True, invalid inputs will raise `rich.internals.ValidationError`, else
                                                the error will be reported onto the console. Defaults to True.
        raise_type_conversion_fail (bool, optional): If True, invalid inputs will raise `rich.internals.ConversionError`, else
                                                     the error will be reported onto the console. Defaults to True.
        initial_value (str, optional): If present, the value is placed in the prompt as the default value.
        completion (Callable[[str], List[str]], optional): Returns completion options for the current input.
        instructions (str, optional): Rich friendly text shown below the input. Pass `None` to hide it.
                                      Defaults to '([bold]enter[/bold] to confirm)'.
        config (Config, optional): Configuration to use. Defaults to `Config()`.

    Raises:
        ValidationError: Raised if validation with provided validator fails
        ConversionError: Raised if the value cannot be converted to provided type
        KeyboardInterrupt: Raised when keyboard interrupt is encountered and `config.raise_on_interrupt` is True

    Returns:
        Union[T, str]: Returns a value formatted as provided type or string if no type is provided
    """
    config = config or Config()

    renderer = partial(_render_prompt, secure, instructions)

    element = qprompt.Prompt(
        state=qprompt.PromptState(
            title=prompt,
            value=(initial_value or ''),
            cursor_position=len(initial_value or ''),
        ),
        renderer=renderer,
        transient=config.transient,
        console=config.console,
    )

    with element.displayed():
        while True:
            key = get_key()
            new_state = element.state
            new_state.completion.options = completion(new_state.value) if completion else []
            new_state = _prompt_key_handler(new_state, key)
            if new_state.exit:
                if key == Keys.ESC:
                    if config.raise_on_escape:
                        raise Abort(key)
                    return None
                try:
                    res = _validate_prompt_value(
                        value=[*(new_state.value or '')],
                        target_type=target_type,
                        validator=validator,
                        secure=secure,
                    )
                    return res
                except ValidationError as e:
                    if raise_validation_fail:
                        raise e

                    new_state.error = str(e)
                except ConversionError as e:
                    if raise_type_conversion_fail:
                        raise e
                    new_state.error = str(e)
            elif new_state.abort:
                if config.raise_on_interrupt:
                    raise KeyboardInterrupt()
                return None
            element.state = new_state


T = TypeVar('T')

Options = Union[List[T], Dict[str, List[T]]]
Index = Union[int, SectionedPosition]


def _auto_page_size(console: Console, reserved_lines: int, title: str, sections: List[Optional[str]], filterable: bool) -> int:
    # ponytail: reserves a line for every section header, conservative when headers are spread over pages
    reserved_lines += (title.count('\n') + 1 if title or filterable else 0) + len(set(sections) - {None})
    return max(1, console.size.height - reserved_lines)


@overload
def select(
    options: List[T],
    *,
    preprocessor: Callable[[T], str] = ...,
    cursor: str = ...,
    cursor_style: str = ...,
    cursor_index: int = ...,
    return_index: Literal[False] = ...,
    strict: bool = ...,
    pagination: bool = ...,
    page_size: Optional[int] = ...,
    title: str = ...,
    instructions: Optional[str] = ...,
    filterable: bool = ...,
    config: Optional[Config] = ...,
) -> Optional[T]: ...


@overload
def select(
    options: List[T],
    *,
    preprocessor: Callable[[T], str] = ...,
    cursor: str = ...,
    cursor_style: str = ...,
    cursor_index: int = ...,
    return_index: Literal[True],
    strict: bool = ...,
    pagination: bool = ...,
    page_size: Optional[int] = ...,
    title: str = ...,
    instructions: Optional[str] = ...,
    filterable: bool = ...,
    config: Optional[Config] = ...,
) -> Optional[int]: ...


@overload
def select(
    options: Dict[str, List[T]],
    *,
    preprocessor: Callable[[T], str] = ...,
    cursor: str = ...,
    cursor_style: str = ...,
    cursor_index: SectionedPosition = ...,
    return_index: Literal[False] = ...,
    strict: bool = ...,
    pagination: bool = ...,
    page_size: Optional[int] = ...,
    title: str = ...,
    instructions: Optional[str] = ...,
    filterable: bool = ...,
    config: Optional[Config] = ...,
) -> Optional[T]: ...


@overload
def select(
    options: Dict[str, List[T]],
    *,
    preprocessor: Callable[[T], str] = ...,
    cursor: str = ...,
    cursor_style: str = ...,
    cursor_index: SectionedPosition = ...,
    return_index: Literal[True],
    strict: bool = ...,
    pagination: bool = ...,
    page_size: Optional[int] = ...,
    title: str = ...,
    instructions: Optional[str] = ...,
    filterable: bool = ...,
    config: Optional[Config] = ...,
) -> Optional[SectionedPosition]: ...


@overload
def select(
    options: List[T],
    *,
    preprocessor: Callable[[T], str] = ...,
    cursor: str = ...,
    cursor_style: str = ...,
    cursor_index: int = ...,
    return_index: bool = ...,
    strict: bool = ...,
    pagination: bool = ...,
    page_size: Optional[int] = ...,
    title: str = ...,
    instructions: Optional[str] = ...,
    filterable: bool = ...,
    config: Optional[Config] = ...,
) -> Optional[Union[T, int]]: ...


@overload
def select(
    options: Dict[str, List[T]],
    *,
    preprocessor: Callable[[T], str] = ...,
    cursor: str = ...,
    cursor_style: str = ...,
    cursor_index: SectionedPosition = ...,
    return_index: bool = ...,
    strict: bool = ...,
    pagination: bool = ...,
    page_size: Optional[int] = ...,
    title: str = ...,
    instructions: Optional[str] = ...,
    filterable: bool = ...,
    config: Optional[Config] = ...,
) -> Optional[Union[T, SectionedPosition]]: ...


def select(
    options: Options,
    *,
    preprocessor: Callable[[T], str] = lambda val: str(val),
    cursor: str = '>',
    cursor_style: str = 'pink1',
    cursor_index: Optional[Index] = None,
    return_index: bool = False,
    strict: bool = False,
    pagination: bool = False,
    page_size: Optional[int] = None,
    title: str = '',
    instructions: Optional[str] = _CONFIRM_INSTRUCTIONS,
    filterable: bool = False,
    config: Optional[Config] = None,
) -> Any:
    """A prompt that allows selecting one option from a list of options

    Args:
        options (Union[List[Union[str, T]], Dict[str, List[Union[str, T]]]]): A list of options to select from. If `preprocessor` is
                                       left as default (not passed), it needs to be a list of strings or objects with a `__str__` method.
                                       Otherwise, you can pass a `preprocessor` to create a string representation of arbitrary
                                       data-structures. Pass a dict of `{section_name: options}` to show options in sections.
        preprocessor (Callable[[T], str]): A callable that can be used to preprocess the list of options prior to printing.
                                           For example, if you passed a `Person` object with `name` attribute, preprocessor
                                           could be `lambda person: person.name` to just show the content of `name` attribute
                                           in the select dialog. Defaults to `lambda val: val`
        cursor (str, optional): Cursor that is going to appear in front of currently selected option. Defaults to '> '.
        cursor_style (str, optional): Rich friendly style for the cursor. Defaults to 'pink1'.
        cursor_index (Union[int, Tuple[str, int]], optional): Option can be preselected based on its list index.
                                                              For sectioned options, it must be `(section_name, index_in_section)`. Defaults to the first option.
        return_index (bool, optional): If `True`, `select` will return the index of selected element in options.
                                       For sectioned options, it's `(section_name, index_in_section)`. Defaults to `False`.
        strict (bool, optional): If empty `options` is provided and strict is `False`, None will be returned,
        if it's `True`, `ValueError` will be thrown. Defaults to False.
        pagination (bool, optional): If `True`, pagination will be used. Defaults to False.
        page_size (Optional[int], optional): Number of options to show on a single page if pagination is enabled.
                                             If `None`, the page size is derived automatically from the terminal height.
                                             Pagination is also enabled automatically when options exceed the terminal height.
                                             Defaults to None.
        title (str, optional): Rich friendly text shown above the options. Defaults to ''.
        instructions (str, optional): Rich friendly text shown below the options. Pass `None` to hide it.
                                      Defaults to '([bold]enter[/bold] to confirm)'.
        filterable (bool, optional): If `True`, typing filters the options (case-insensitive substring of the displayed text)
                                     and backspace edits the filter. Keys bound in `config.keys` keep their action. Defaults to False.
        config (Config, optional): Configuration to use. Defaults to `Config()`.

    Raises:
        ValueError: Thrown if no `options` are provided and strict is `True`
        KeyboardInterrupt: Raised when keyboard interrupt is encountered and `config.raise_on_interrupt` is True

    Returns:
        Union[int, Tuple[str, int], str, None]: Selected value or the index of a selected option or `None`
    """
    config = config or Config()
    keys = config.keys
    flat_options, sections, positions = _flatten_options(options)

    if not flat_options:
        if strict:
            raise ValueError('`options` cannot be empty')
        return None
    if cursor_style in ['', None]:
        warnings.warn('`cursor_style` should be a valid style, defaulting to `white`')
        cursor_style = 'white'

    labels = _option_labels(flat_options, preprocessor) if filterable else []
    effective_page_size = page_size if page_size is not None else _auto_page_size(config.console, 6, title, sections, filterable)
    effective_pagination = pagination or (page_size is None and len(flat_options) > effective_page_size)

    renderer = partial(_render_select, preprocessor, cursor_style, cursor, title, instructions, sections, labels)

    element = qselect.Select(
        qselect.SelectState(
            options=flat_options,
            title=title,
            index=_to_flat_index(positions, cursor_index),
            pagination=effective_pagination,
            page_size=effective_page_size,
        ),
        renderer=renderer,
        transient=config.transient,
        console=config.console,
    )

    with element.displayed():

        while True:
            keypress = get_key()

            state = element.state
            if keys.is_navigation(keypress):
                element.state = _navigate_select(state, keypress=keypress, keys=keys, visible=_visible_indexes(state, labels))
            elif keypress in keys.confirm:
                if state.index not in _visible_indexes(state, labels):
                    continue
                if return_index:
                    return positions[element.state.index]
                return flat_options[element.state.index]
            elif keypress in keys.escape:
                if config.raise_on_escape:
                    raise Abort(keypress)
                return None
            elif keypress in keys.interrupt:
                if config.raise_on_interrupt:
                    raise KeyboardInterrupt()
                return None
            elif filterable and _update_filter(state, keypress, keys, labels):
                element.state = state


@overload
def select_multiple(
    options: List[T],
    *,
    preprocessor: Callable[[T], str] = ...,
    tick_character: str = ...,
    tick_style: str = ...,
    cursor_style: str = ...,
    ticked_indices: Optional[List[int]] = ...,
    cursor_index: int = ...,
    minimal_count: int = ...,
    maximal_count: Optional[int] = ...,
    return_indices: Literal[False] = ...,
    strict: bool = ...,
    pagination: bool = ...,
    page_size: Optional[int] = ...,
    title: str = ...,
    instructions: Optional[str] = ...,
    filterable: bool = ...,
    config: Optional[Config] = ...,
) -> List[T]: ...


@overload
def select_multiple(
    options: List[T],
    *,
    preprocessor: Callable[[T], str] = ...,
    tick_character: str = ...,
    tick_style: str = ...,
    cursor_style: str = ...,
    ticked_indices: Optional[List[int]] = ...,
    cursor_index: int = ...,
    minimal_count: int = ...,
    maximal_count: Optional[int] = ...,
    return_indices: Literal[True],
    strict: bool = ...,
    pagination: bool = ...,
    page_size: Optional[int] = ...,
    title: str = ...,
    instructions: Optional[str] = ...,
    filterable: bool = ...,
    config: Optional[Config] = ...,
) -> List[int]: ...


@overload
def select_multiple(
    options: Dict[str, List[T]],
    *,
    preprocessor: Callable[[T], str] = ...,
    tick_character: str = ...,
    tick_style: str = ...,
    cursor_style: str = ...,
    ticked_indices: Optional[List[SectionedPosition]] = ...,
    cursor_index: SectionedPosition = ...,
    minimal_count: int = ...,
    maximal_count: Optional[int] = ...,
    return_indices: Literal[False] = ...,
    strict: bool = ...,
    pagination: bool = ...,
    page_size: Optional[int] = ...,
    title: str = ...,
    instructions: Optional[str] = ...,
    filterable: bool = ...,
    config: Optional[Config] = ...,
) -> List[T]: ...


@overload
def select_multiple(
    options: Dict[str, List[T]],
    *,
    preprocessor: Callable[[T], str] = ...,
    tick_character: str = ...,
    tick_style: str = ...,
    cursor_style: str = ...,
    ticked_indices: Optional[List[SectionedPosition]] = ...,
    cursor_index: SectionedPosition = ...,
    minimal_count: int = ...,
    maximal_count: Optional[int] = ...,
    return_indices: Literal[True],
    strict: bool = ...,
    pagination: bool = ...,
    page_size: Optional[int] = ...,
    title: str = ...,
    instructions: Optional[str] = ...,
    filterable: bool = ...,
    config: Optional[Config] = ...,
) -> List[SectionedPosition]: ...


@overload
def select_multiple(
    options: List[T],
    *,
    preprocessor: Callable[[T], str] = ...,
    tick_character: str = ...,
    tick_style: str = ...,
    cursor_style: str = ...,
    ticked_indices: Optional[List[int]] = ...,
    cursor_index: int = ...,
    minimal_count: int = ...,
    maximal_count: Optional[int] = ...,
    return_indices: bool = ...,
    strict: bool = ...,
    pagination: bool = ...,
    page_size: Optional[int] = ...,
    title: str = ...,
    instructions: Optional[str] = ...,
    filterable: bool = ...,
    config: Optional[Config] = ...,
) -> List[Union[T, int]]: ...


@overload
def select_multiple(
    options: Dict[str, List[T]],
    *,
    preprocessor: Callable[[T], str] = ...,
    tick_character: str = ...,
    tick_style: str = ...,
    cursor_style: str = ...,
    ticked_indices: Optional[List[SectionedPosition]] = ...,
    cursor_index: SectionedPosition = ...,
    minimal_count: int = ...,
    maximal_count: Optional[int] = ...,
    return_indices: bool = ...,
    strict: bool = ...,
    pagination: bool = ...,
    page_size: Optional[int] = ...,
    title: str = ...,
    instructions: Optional[str] = ...,
    filterable: bool = ...,
    config: Optional[Config] = ...,
) -> List[Union[T, SectionedPosition]]: ...


def select_multiple(
    options: Options,
    *,
    preprocessor: Callable[[T], str] = lambda val: str(val),
    tick_character: str = '✓',
    tick_style: str = 'pink1',
    cursor_style: str = 'pink1',
    ticked_indices: Optional[Sequence[Index]] = None,
    cursor_index: Optional[Index] = None,
    minimal_count: int = 0,
    maximal_count: Optional[int] = None,
    return_indices: bool = False,
    strict: bool = False,
    pagination: bool = False,
    page_size: Optional[int] = None,
    title: str = '',
    instructions: Optional[str] = _SELECT_MULTIPLE_INSTRUCTIONS,
    filterable: bool = False,
    config: Optional[Config] = None,
) -> List[Any]:
    """A prompt that allows selecting multiple options from a list of options

    Args:
        options (Union[List[Union[str, T]], Dict[str, List[Union[str, T]]]]): A list of options to select from. If `preprocessor` is
                                       left as default (not passed), it needs to be a list of strings or objects with a `__str__` method.
                                       Otherwise, you can pass a `preprocessor` to create a string representation of arbitrary
                                       data-structures. Pass a dict of `{section_name: options}` to show options in sections.
        preprocessor (Callable[[T], str]): A callable that can be used to preprocess the list of options prior to printing.
                                           For example, if you passed a `Person` object with `name` attribute, preprocessor
                                           could be `lambda person: person.name` to just show the content of `name` attribute
                                           in the select_multiple dialog. Defaults to `lambda val: val`
        tick_character (str, optional): Character that will be used as a tick in a checkbox. Defaults to 'x'.
        tick_style (str, optional): Rich friendly style for the tick character. Defaults to 'pink1'.
        cursor_style (str, optional): Rich friendly style for the option when the cursor is currently on it. Defaults to 'pink1'.
        ticked_indices (Optional[List[Union[int, Tuple[str, int]]]], optional): Indices of options that are pre-ticked when the prompt
                                                                                appears. For sectioned options, they must be
                                                                                `(section_name, index_in_section)`. Defaults to None.
        cursor_index (Union[int, Tuple[str, int]], optional): Index of the option cursor starts at.
                                                              For sectioned options, it must be `(section_name, index_in_section)`. Defaults to the first option.
        minimal_count (int, optional): Minimal count of options that need to be selected. Defaults to 0.
        maximal_count (Optional[int], optional): Maximal count of options that need to be selected. Defaults to None.
        return_indices (bool, optional): If `True`, `select_multiple` will return the indices of ticked elements in options.
                                         For sectioned options, they are `(section_name, index_in_section)`. Defaults to `False`.
        strict (bool, optional): If empty `options` is provided and strict is `False`, None will be returned,
                                 if it's `True`, `ValueError` will be thrown. Defaults to False.
        pagination (bool, optional): If `True`, pagination will be used. Defaults to False.
        page_size (Optional[int], optional): Number of options to show on a single page if pagination is enabled.
                                             If `None`, the page size is derived automatically from the terminal height.
                                             Pagination is also enabled automatically when options exceed the terminal height.
                                             Defaults to None.
        title (str, optional): Rich friendly text shown above the options. Defaults to ''.
        instructions (str, optional): Rich friendly text shown below the options. Pass `None` to hide it.
        filterable (bool, optional): If `True`, typing filters the options (case-insensitive substring of the displayed text)
                                     and backspace edits the filter. Keys bound in `config.keys` keep their action, so space still ticks. Defaults to False.
        config (Config, optional): Configuration to use. Defaults to `Config()`.

    Raises:
        KeyboardInterrupt: Raised when keyboard interrupt is encountered and `config.raise_on_interrupt` is True

    Returns:
        Union[List[str], List[int], List[Tuple[str, int]]]: A list of selected values or indices of selected options
    """
    config = config or Config()
    flat_options, sections, positions = _flatten_options(options)

    if not flat_options:
        if strict:
            raise ValueError('`options` cannot be empty')
        return []
    if cursor_style in ['', None]:
        warnings.warn('`cursor_style` should be a valid style, defaulting to `white`')
        cursor_style = 'white'
    if tick_style in ['', None]:
        warnings.warn('`tick_style` should be a valid style, defaulting to `white`')
        tick_style = 'white'

    labels = _option_labels(flat_options, preprocessor) if filterable else []
    effective_page_size = page_size if page_size is not None else _auto_page_size(config.console, 1, title, sections, filterable)
    effective_pagination = pagination or (page_size is None and len(flat_options) > effective_page_size)

    renderer = partial(
        _render_select_multiple, preprocessor, tick_character, tick_style, cursor_style, title, instructions, sections, labels
    )

    element = qselect.Select(
        qselect.SelectState(
            options=flat_options,
            title=title,
            select_multiple=True,
            index=_to_flat_index(positions, cursor_index),
            selected_indexes=[_to_flat_index(positions, i) for i in ticked_indices or []],
            pagination=effective_pagination,
            page_size=effective_page_size,
        ),
        renderer=renderer,
        transient=config.transient,
        console=config.console,
    )

    with element.displayed():
        while True:
            keypress = get_key()
            new_state = element.state
            new_state.error = ''

            new_state = _navigate_select_multiple(new_state, keypress, minimal_count, maximal_count, config, labels if filterable else None)
            if new_state.exit or new_state.abort:
                break
            element.state = new_state
        if return_indices:
            return [positions[i] for i in new_state.selected_indexes]
        return [flat_options[i] for i in new_state.selected_indexes]


def confirm(
    question: str,
    *,
    yes_text: str = 'Yes',
    no_text: str = 'No',
    has_to_match_case: bool = False,
    enter_empty_confirms: bool = True,
    default_is_yes: bool = False,
    cursor: str = '>',
    cursor_style: str = 'pink1',
    char_prompt: bool = True,
    instructions: Optional[str] = _CONFIRM_INSTRUCTIONS,
    config: Optional[Config] = None,
) -> Optional[bool]:
    """A prompt that asks a question and offers two responses

    Args:
        question (str): Question to be asked
        yes_text (str, optional): Text of the positive response. Defaults to 'Yes'.
        no_text (str, optional): Text of the negative response. Defaults to 'No'.
        has_to_match_case (bool, optional): Check if typed response matches case. Defaults to False.
        enter_empty_confirms (bool, optional): No response is confirmation. Defaults to True.
        default_is_yes (bool, optional): Default is Yes. Defaults to False.
        cursor (str, optional): What character(s) to use as a cursor. Defaults to '> '.
        cursor_style (str, optional): Rich friendly style for the cursor. Defaults to 'pink1'.
        char_prompt (bool, optional): Print [Y/n] after the question. Defaults to True.
        instructions (str, optional): Rich friendly text shown below the responses. Pass `None` to hide it.
                                      Defaults to '([bold]enter[/bold] to confirm)'.
        config (Config, optional): Configuration to use. Defaults to `Config()`.

    Raises:
        KeyboardInterrupt: Raised when keyboard interrupt is encountered and `config.raise_on_interrupt` is True

    Returns:
        Optional[bool]
    """
    config = config or Config()
    keys = config.keys
    console = config.console
    rendered = ''
    with _cursor_hidden(console), Live(rendered, console=console, auto_refresh=False, transient=config.transient) as live:
        if cursor_style in ['', None]:
            warnings.warn('`cursor_style` should be a valid style, defaulting to `white`')
            cursor_style = 'white'
        is_yes = default_is_yes
        is_selected = enter_empty_confirms
        current_message = ''
        yn_prompt = f' ({yes_text[0]}/{no_text[0]}) ' if char_prompt else ': '
        selected_prefix = f'[{cursor_style}]{cursor}[/{cursor_style}] '
        deselected_prefix = (' ' * len(cursor)) + ' '
        while True:
            yes = is_yes and is_selected
            no = not is_yes and is_selected
            question_line = f'{question}{yn_prompt}{current_message}'
            yes_prefix = selected_prefix if yes else deselected_prefix
            no_prefix = selected_prefix if no else deselected_prefix
            rendered = f'{question_line}\n{yes_prefix}{yes_text}\n{no_prefix}{no_text}' + (f'\n\n{instructions}' if instructions else '')
            _update_rendered(live, rendered)

            keypress = get_key()
            if keypress in keys.interrupt:
                if config.raise_on_interrupt:
                    raise KeyboardInterrupt()
                return None
            elif keypress in keys.down or keypress in keys.up:
                is_yes = not is_yes
                is_selected = True
                current_message = yes_text if is_yes else no_text
            elif keypress in keys.backspace:
                if current_message:
                    current_message = current_message[:-1]
            elif keypress in keys.confirm:
                if is_selected:
                    break
            elif keypress in keys.tab:
                if is_selected:
                    current_message = yes_text if is_yes else no_text
            elif keypress in keys.escape:
                if config.raise_on_escape:
                    raise Abort(keypress)
                return None
            else:
                current_message += str(keypress)
                match_yes = yes_text
                match_no = no_text
                match_text = current_message
                if not has_to_match_case:
                    match_yes = match_yes.upper()
                    match_no = match_no.upper()
                    match_text = match_text.upper()
                if match_no.startswith(match_text):
                    is_selected = True
                    is_yes = False
                elif match_yes.startswith(match_text):
                    is_selected = True
                    is_yes = True
                else:
                    is_selected = False
        return is_selected and is_yes
