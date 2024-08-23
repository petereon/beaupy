#! /usr/bin/env python3
"""
A Python library of interactive CLI elements you have been looking for
"""

__license__ = 'MIT'

import math
import warnings
from functools import partial
from typing import Any, Callable, List, Optional, Tuple, Type, Union

from questo import prompt as qprompt
from questo import select as qselect
from rich.console import Console
from rich.live import Live
from yakh import get_key
from yakh.key import Key, Keys

from beaupy._internals import (
    Abort,
    ConversionError,
    TargetType,
    ValidationError,
    _cursor_hidden,
    _paginate_back,
    _paginate_forward,
    _prompt_key_handler,
    _render_prompt,
    _render_select,
    _render_select_multiple,
    _update_rendered,
    _validate_prompt_value,
)

console = Console()


class DefaultKeys:
    """A map of default keybindings.

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
        home(List[Union[Tuple[int, ...], str]]): Keys that move to the beginning of the context.
        end(List[Union[Tuple[int, ...], str]]): Keys that move to the end of the context.
    """

    escape: List[Union[Tuple[int, ...], str]] = [Keys.ESC]
    select: List[Union[Tuple[int, ...], str]] = [' ']
    confirm: List[Union[Tuple[int, ...], str]] = [Keys.ENTER]
    backspace: List[Union[Tuple[int, ...], str]] = [Keys.BACKSPACE]
    delete: List[Union[Tuple[int, ...], str]] = [Keys.DELETE]
    down: List[Union[Tuple[int, ...], str]] = [Keys.DOWN_ARROW, Keys.NUMPAD_DOWN_ARROW]
    up: List[Union[Tuple[int, ...], str]] = [Keys.UP_ARROW, Keys.NUMPAD_UP_ARROW]
    left: List[Union[Tuple[int, ...], str]] = [Keys.LEFT_ARROW, Keys.NUMPAD_LEFT_ARROW]
    right: List[Union[Tuple[int, ...], str]] = [Keys.RIGHT_ARROW, Keys.NUMPAD_RIGHT_ARROW]
    tab: List[Union[Tuple[int, ...], str]] = [Keys.TAB]
    home: List[Union[Tuple[int, ...], str]] = [Keys.HOME]
    end: List[Union[Tuple[int, ...], str]] = [Keys.END]
    interrupt: List[Union[Tuple[int, ...], str]] = [Keys.CTRL_C]
    select_all: List[Union[Tuple[int, ...], str]] = ['a']


class Config:
    """A map of default configuration

    Attributes:
        raise_on_interrupt(bool): If True, functions will raise KeyboardInterrupt whenever one is encountered when waiting for input,
        otherwise, they will return some sane alternative to their usual return. For `select`, `prompt` and `confirm` this means `None`,
        while for `select_multiple` it means an empty list - `[]`. Defaults to False.
        raise_on_escape(bool): If True, functions will raise Abort whenever the escape key is encountered when waiting for input, otherwise,
        they will return some sane alternative to their usual return. For `select`, `prompt` and `confirm` this means `None`, while for
        `select_multiple` it means an empty list - `[]`.  Defaults to False.
        transient(bool): If False, elements will remain displayed after its context has ended. Defaults to True.
    """

    raise_on_interrupt: bool = False
    raise_on_escape: bool = False
    transient: bool = True


_navigation_keys = [DefaultKeys.up, DefaultKeys.down, DefaultKeys.right, DefaultKeys.left, DefaultKeys.home, DefaultKeys.end]


def _navigate_select(
    state: qselect.SelectState,
    keypress: Key,
) -> qselect.SelectState:

    total_options = len(state.options)

    page: int = state.index // state.page_size + 1
    total_pages = math.ceil(len(state.options) / state.page_size)

    show_from = (page - 1) * state.page_size
    show_to = min(show_from + state.page_size, len(state.options))

    index = state.index

    if keypress in DefaultKeys.up:
        if index <= show_from and state.pagination:
            page = _paginate_back(page, total_pages)
        index -= 1
        index = index % total_options
    elif keypress in DefaultKeys.down:
        if index > show_to - 2 and state.pagination:
            page = _paginate_forward(page, total_pages)
        index += 1
        index = index % total_options
    elif keypress in DefaultKeys.right and state.pagination:
        page = _paginate_forward(page, total_pages)
        index = (page - 1) * state.page_size
    elif keypress in DefaultKeys.left and state.pagination:
        page = _paginate_back(page, total_pages)
        index = (page - 1) * state.page_size
    elif keypress in DefaultKeys.home:
        page = 1
        index = 0
    elif keypress in DefaultKeys.end:
        page = total_pages
        index = total_options - 1

    state.index = index
    return state


def _navigate_select_multiple(
    state: qselect.SelectState, keypress: Key, minimal_count: int, maximal_count: Union[int, None]
) -> qselect.SelectState:
    if keypress in DefaultKeys.interrupt:
        state.selected_indexes = []
        if Config.raise_on_interrupt:
            raise KeyboardInterrupt()
        state.abort = True

    elif any([keypress in navigation_keys for navigation_keys in _navigation_keys]):
        state = _navigate_select(state, keypress=keypress)
    elif keypress in DefaultKeys.select_all:
        if len(state.selected_indexes) == (maximal_count if maximal_count is not None else len(state.options)):
            state.selected_indexes = []
        else:
            if maximal_count is not None:
                state.selected_indexes = list(range(maximal_count))
                state.error = f'Must select at most {maximal_count} options'
            else:
                state.selected_indexes = list(range(len(state.options)))
    elif keypress in DefaultKeys.select:
        if state.index in state.selected_indexes:
            state.selected_indexes.remove(state.index)
        else:
            if maximal_count is not None and len(state.selected_indexes) + 1 > maximal_count:
                state.error = f'Must select at most {maximal_count} options'
            else:
                state.selected_indexes.append(state.index)
    elif keypress in DefaultKeys.confirm:
        if minimal_count > len(state.selected_indexes):
            state.error = f'Must select at least {minimal_count} options'
        else:
            state.exit = True
    elif keypress in DefaultKeys.escape:
        state.selected_indexes = []
        if Config.raise_on_escape:
            raise Abort(keypress)
        state.exit = True
    return state


def prompt(
    prompt: str,
    target_type: Type[TargetType] = str,
    validator: Callable[[TargetType], bool] = lambda input: True,
    secure: bool = False,
    raise_validation_fail: bool = True,
    raise_type_conversion_fail: bool = True,
    initial_value: Optional[str] = None,
    completion: Optional[Callable[[str], List[str]]] = None,
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

    Raises:
        ValidationError: Raised if validation with provided validator fails
        ConversionError: Raised if the value cannot be converted to provided type
        KeyboardInterrupt: Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True

    Returns:
        Union[T, str]: Returns a value formatted as provided type or string if no type is provided
    """

    renderer = partial(_render_prompt, secure)

    element = qprompt.Prompt(
        state=qprompt.PromptState(
            title=prompt,
            value=(initial_value or ''),
            cursor_position=len(initial_value or ''),
        ),
        renderer=renderer,
        transient=Config.transient
    )

    with element.displayed():
        while True:
            key = get_key()
            new_state = element.state
            new_state.completion.options = completion(new_state.value) if completion else []
            new_state = _prompt_key_handler(new_state, key)
            if new_state.exit:
                if key == Keys.ESC:
                    if Config.raise_on_escape:
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
                if Config.raise_on_interrupt:
                    raise KeyboardInterrupt()
                return None
            element.state = new_state


def select(
    options: List[Union[Tuple[int, ...], str]],
    preprocessor: Callable[[Any], Any] = lambda val: val,
    cursor: str = '>',
    cursor_style: str = 'pink1',
    cursor_index: int = 0,
    return_index: bool = False,
    strict: bool = False,
    pagination: bool = False,
    page_size: int = 5,
) -> Union[int, Any, None]:
    """A prompt that allows selecting one option from a list of options

    Args:
        options (List[Union[Tuple[int, ...], str]]): A list of options to select from
        preprocessor (Callable[[Any], Any]): A callable that can be used to preprocess the list of options prior to printing.
                                             For example, if you passed a `Person` object with `name` attribute, preprocessor
                                             could be `lambda person: person.name` to just show the content of `name` attribute
                                             in the select dialog. Defaults to `lambda val: val`
        cursor (str, optional): Cursor that is going to appear in front of currently selected option. Defaults to '> '.
        cursor_style (str, optional): Rich friendly style for the cursor. Defaults to 'pink1'.
        cursor_index (int, optional): Option can be preselected based on its list index. Defaults to 0.
        return_index (bool, optional): If `True`, `select` will return the index of selected element in options. Defaults to `False`.
        strict (bool, optional): If empty `options` is provided and strict is `False`, None will be returned,
        if it's `True`, `ValueError` will be thrown. Defaults to False.
        pagination (bool, optional): If `True`, pagination will be used. Defaults to False.
        page_size (int, optional): Number of options to show on a single page if pagination is enabled. Defaults to 5.

    Raises:
        ValueError: Thrown if no `options` are provided and strict is `True`
        KeyboardInterrupt: Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True

    Returns:
        Union[int, str, None]: Selected value or the index of a selected option or `None`
    """

    if not options:
        if strict:
            raise ValueError('`options` cannot be empty')
        return None
    if cursor_style in ['', None]:
        warnings.warn('`cursor_style` should be a valid style, defaulting to `white`')
        cursor_style = 'white'

    renderer = partial(_render_select, preprocessor, cursor_style, cursor)

    element = qselect.Select(
        qselect.SelectState(
            options=options,
            title='',
            index=cursor_index,
            pagination=pagination,
            page_size=page_size,
        ),
        renderer=renderer,
        transient=Config.transient
    )

    with element.displayed():

        while True:
            keypress = get_key()

            if any([keypress in navigation_keys for navigation_keys in _navigation_keys]):
                element.state = _navigate_select(element.state, keypress=keypress)
            elif keypress in DefaultKeys.confirm:
                if return_index:
                    return element.state.index
                return options[element.state.index]
            elif keypress in DefaultKeys.escape:
                if Config.raise_on_escape:
                    raise Abort(keypress)
                return None
            elif keypress in DefaultKeys.interrupt:
                if Config.raise_on_interrupt:
                    raise KeyboardInterrupt()
                return None


def select_multiple(
    options: List[Union[Tuple[int, ...], str]],
    preprocessor: Callable[[Any], Any] = lambda val: val,
    tick_character: str = '✓',
    tick_style: str = 'pink1',
    cursor_style: str = 'pink1',
    ticked_indices: Optional[List[int]] = None,
    cursor_index: int = 0,
    minimal_count: int = 0,
    maximal_count: Optional[int] = None,
    return_indices: bool = False,
    strict: bool = False,
    pagination: bool = False,
    page_size: int = 5,
) -> List[Union[int, Any]]:
    """A prompt that allows selecting multiple options from a list of options

    Args:
        options (List[Union[Tuple[int, ...], str]]): A list of options to select from
        preprocessor (Callable[[Any], Any]): A callable that can be used to preprocess the list of options prior to printing.
                                             For example, if you passed a `Person` object with `name` attribute, preprocessor
                                             could be `lambda person: person.name` to just show the content of `name` attribute
                                             in the select dialog. Defaults to `lambda val: val`
        tick_character (str, optional): Character that will be used as a tick in a checkbox. Defaults to 'x'.
        tick_style (str, optional): Rich friendly style for the tick character. Defaults to 'pink1'.
        cursor_style (str, optional): Rich friendly style for the option when the cursor is currently on it. Defaults to 'pink1'.
        ticked_indices (Optional[List[int]], optional): Indices of options that are pre-ticked when the prompt appears. Defaults to None.
        cursor_index (int, optional): Index of the option cursor starts at. Defaults to 0.
        minimal_count (int, optional): Minimal count of options that need to be selected. Defaults to 0.
        maximal_count (Optional[int], optional): Maximal count of options that need to be selected. Defaults to None.
        return_indices (bool, optional): If `True`, `select_multiple` will return the indices
                                         of ticked elements in options. Defaults to `False`.
        strict (bool, optional): If empty `options` is provided and strict is `False`, None will be returned,
                                 if it's `True`, `ValueError` will be thrown. Defaults to False.
        pagination (bool, optional): If `True`, pagination will be used. Defaults to False.
        page_size (int, optional): Number of options to show on a single page if pagination is enabled. Defaults to 5.

    Raises:
        KeyboardInterrupt: Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True

    Returns:
        Union[List[str], List[int]]: A list of selected values or indices of selected options
    """

    if not options:
        if strict:
            raise ValueError('`options` cannot be empty')
        return []
    if cursor_style in ['', None]:
        warnings.warn('`cursor_style` should be a valid style, defaulting to `white`')
        cursor_style = 'white'
    if tick_style in ['', None]:
        warnings.warn('`tick_style` should be a valid style, defaulting to `white`')
        tick_style = 'white'
    if ticked_indices is None:
        ticked_indices = []

    renderer = partial(_render_select_multiple, preprocessor, tick_character, tick_style, cursor_style)

    element = qselect.Select(
        qselect.SelectState(
            options=options,
            title='',
            select_multiple=True,
            index=cursor_index,
            selected_indexes=ticked_indices,
            pagination=pagination,
            page_size=page_size,
        ),
        renderer=renderer,
        transient=Config.transient
    )

    with element.displayed():
        while True:
            keypress = get_key()
            new_state = element.state
            new_state.error = ''

            new_state = _navigate_select_multiple(new_state, keypress, minimal_count, maximal_count)
            if new_state.exit or new_state.abort:
                break
            element.state = new_state
        if return_indices:
            return new_state.selected_indexes  # type: ignore
        return [options[i] for i in new_state.selected_indexes]


def confirm(
    question: str,
    yes_text: str = 'Yes',
    no_text: str = 'No',
    has_to_match_case: bool = False,
    enter_empty_confirms: bool = True,
    default_is_yes: bool = False,
    cursor: str = '>',
    cursor_style: str = 'pink1',
    char_prompt: bool = True,
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

    Raises:
        KeyboardInterrupt: Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True

    Returns:
        Optional[bool]
    """
    rendered = ''
    with _cursor_hidden(console), Live(rendered, console=console, auto_refresh=False, transient=Config.transient) as live:
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
            rendered = f'{question_line}\n{yes_prefix}{yes_text}\n{no_prefix}{no_text}\n\n([bold]enter[/bold] to confirm)'
            _update_rendered(live, rendered)

            keypress = get_key()
            if keypress in DefaultKeys.interrupt:
                if Config.raise_on_interrupt:
                    raise KeyboardInterrupt()
                return None
            elif keypress in DefaultKeys.down or keypress in DefaultKeys.up:
                is_yes = not is_yes
                is_selected = True
                current_message = yes_text if is_yes else no_text
            elif keypress in DefaultKeys.backspace:
                if current_message:
                    current_message = current_message[:-1]
            elif keypress in DefaultKeys.confirm:
                if is_selected:
                    break
            elif keypress in DefaultKeys.tab:
                if is_selected:
                    current_message = yes_text if is_yes else no_text
            elif keypress in DefaultKeys.escape:
                if Config.raise_on_escape:
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
