#! /usr/bin/env python3
"""
A Python library of interactive CLI elements you have been looking for
"""

__license__ = 'MIT'

import warnings
from ast import literal_eval
from typing import Any, Callable, List, Optional, Tuple, Type, Union

from rich.console import Console
from rich.live import Live
from yakh import get_key
from yakh.key import Keys

from beaupy._internals import (
    ConversionError,
    ValidationError,
    _cursor_hidden,
    _format_option_select,
    _render_option_select_multiple,
    _render_prompt,
    _update_rendered,
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


class Config:
    """A map of default configuration

    Attributes:
        raise_on_interrupt(bool): If True, functions will raise KeyboardInterrupt whenever one is encountered when waiting for input,
        otherwise, they will return some sane alternative to their usual return (e.g.: None, [] ). Defaults to False.
    """

    raise_on_interrupt: bool = False


TargetType = Any


def prompt(
    prompt: str,
    target_type: Type[TargetType] = str,
    validator: Callable[[TargetType], bool] = lambda input: True,
    secure: bool = False,
    raise_validation_fail: bool = True,
    raise_type_conversion_fail: bool = True,
    initial_value: Optional[str] = None,
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
    rendered = ''
    with _cursor_hidden(console), Live(rendered, console=console, auto_refresh=False, transient=True) as live:
        value: List[str] = [*initial_value] if initial_value else []
        cursor_index = len(initial_value) if initial_value else 0
        error: str = ''
        while True:
            rendered = _render_prompt(secure, value, prompt, cursor_index, error)
            error = ''
            _update_rendered(live, rendered)
            keypress = get_key()
            if keypress in DefaultKeys.interrupt:
                if Config.raise_on_interrupt:
                    raise KeyboardInterrupt()
                return None
            elif keypress in DefaultKeys.confirm:
                str_value = ''.join(value)
                try:
                    if target_type is bool:
                        result: bool = literal_eval(str_value)
                        if not isinstance(result, bool):
                            raise ValueError()
                    else:
                        result: target_type = target_type(str_value)  # type: ignore
                    if validator(result):
                        return result
                    else:
                        error = f"Input {'<secure_input>' if secure else '`'+str_value+'`'} is invalid"
                        if raise_validation_fail:
                            raise ValidationError(error)
                except ValueError:
                    error = f"Input {'<secure_input>' if secure else '`'+str_value+'`'} cannot be converted to type `{target_type}`"
                    if raise_type_conversion_fail:
                        raise ConversionError(error) from None
            elif keypress in DefaultKeys.backspace:
                if cursor_index > 0:
                    cursor_index -= 1
                    del value[cursor_index]
            elif keypress in DefaultKeys.left:
                if cursor_index > 0:
                    cursor_index -= 1
            elif keypress in DefaultKeys.right:
                if cursor_index < len(value):
                    cursor_index += 1
            elif keypress in DefaultKeys.escape:
                return None
            elif keypress in DefaultKeys.up + DefaultKeys.down:
                pass
            elif keypress in DefaultKeys.home:
                cursor_index = 0
            elif keypress in DefaultKeys.end:
                cursor_index = len(value)
            elif keypress in DefaultKeys.delete:
                if cursor_index < len(value):
                    del value[cursor_index]
            else:
                value.insert(cursor_index, str(keypress))
                cursor_index += 1


Selection = Union[int, Any]


def select(
    options: List[Union[Tuple[int, ...], str]],
    preprocessor: Callable[[Any], Any] = lambda val: val,
    cursor: str = '>',
    cursor_style: str = 'pink1',
    cursor_index: int = 0,
    return_index: bool = False,
    strict: bool = False,
) -> Union[Selection, None]:
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

    Raises:
        ValueError: Thrown if no `options` are povided and strict is `True`
        KeyboardInterrupt: Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True

    Returns:
        Union[int, str, None]: Selected value or the index of a selected option or `None`
    """
    rendered = ''
    with _cursor_hidden(console), Live(rendered, console=console, auto_refresh=False, transient=True) as live:
        if not options:
            if strict:
                raise ValueError('`options` cannot be empty')
            return None
        if cursor_style in ['', None]:
            warnings.warn('`cursor_style` should be a valid style, defaulting to `white`')
            cursor_style = 'white'

        index: int = cursor_index

        while True:
            rendered = (
                '\n'.join(
                    [
                        _format_option_select(
                            i=i, cursor_index=index, option=preprocessor(option), cursor_style=cursor_style, cursor=cursor
                        )
                        for i, option in enumerate(options)
                    ]
                )
                + '\n\n(Confirm with [bold]enter[/bold])'  # noqa: W503
            )
            _update_rendered(live, rendered)
            keypress = get_key()
            if keypress in DefaultKeys.interrupt:
                if Config.raise_on_interrupt:
                    raise KeyboardInterrupt()
                return None
            elif keypress in DefaultKeys.up:
                if index == 0: #Check if index is first option in list.
                    if keypress in DefaultKeys.up: #If key pressed is up, set index to last item in list.
                        index = len(options)
                if index > 0:
                    index -= 1
            elif keypress in DefaultKeys.down:
                if index == len(options)-1: #Chek if index is last option in list.
                    if keypress in DefaultKeys.down: #If key press is "down", set index to 0.
                        index = 0
                        continue # "continue" is added because the if check below is True and "index += 1" is still executed.
                if index < len(options) - 1:
                    index += 1
            elif keypress in DefaultKeys.confirm:
                if return_index:
                    return index
                return options[index]
            elif keypress in DefaultKeys.escape:
                return None


Selections = List[Selection]


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
) -> Selections:
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

    Raises:
        KeyboardInterrupt: Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True

    Returns:
        Union[List[str], List[int]]: A list of selected values or indices of selected options
    """
    rendered = ''
    with _cursor_hidden(console), Live(rendered, console=console, auto_refresh=False, transient=True) as live:
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

        index = cursor_index

        max_index = len(options) - (1 if True else 0)
        error_message = ''
        while True:
            rendered = (
                '\n'.join(
                    [
                        _render_option_select_multiple(
                            option=preprocessor(option),
                            ticked=i in ticked_indices,
                            tick_character=tick_character,
                            tick_style=tick_style,
                            selected=i == index,
                            cursor_style=cursor_style,
                        )
                        for i, option in enumerate(options)
                    ]
                )
                + '\n\n(Mark with [bold]space[/bold], confirm with [bold]enter[/bold])'  # noqa: W503
            )
            if error_message:
                rendered = f'{rendered}\n[red]Error:[/red] {error_message}'
                error_message = ''
            _update_rendered(live, rendered)
            keypress = get_key()
            if keypress in DefaultKeys.interrupt:
                if Config.raise_on_interrupt:
                    raise KeyboardInterrupt()
                return []
            elif keypress in DefaultKeys.up:
                if index == 0: #Check if index is first option in list.
                    if keypress in DefaultKeys.up: #If key pressed is up, set index to last item in list.
                        index = len(options)
                if index > 0:
                    index -= 1
            elif keypress in DefaultKeys.down:
                if index == len(options)-1: #Chek if index is last option in list.
                    if keypress in DefaultKeys.down: #If key press is "down", set index to 0.
                        index = 0
                        continue # "continue" is added because the if check below is True and "index += 1" is still executed.
                if index + 1 <= max_index:
                    index += 1
            elif keypress in DefaultKeys.select:
                if index in ticked_indices:
                    ticked_indices.remove(index)
                elif maximal_count is not None:
                    if len(ticked_indices) + 1 <= maximal_count:
                        ticked_indices.append(index)
                    else:
                        error_message = f'Must select at most {maximal_count} options'
                else:
                    ticked_indices.append(index)
            elif keypress in DefaultKeys.confirm:
                if minimal_count > len(ticked_indices):
                    error_message = f'Must select at least {minimal_count} options'
                else:
                    break
            elif keypress in DefaultKeys.escape:
                return []
        if return_indices:
            return ticked_indices
        return [options[i] for i in ticked_indices]


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
    with _cursor_hidden(console), Live(rendered, console=console, auto_refresh=False, transient=True) as live:
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
            rendered = f'{question_line}\n{yes_prefix}{yes_text}\n{no_prefix}{no_text}\n\n(Confirm with [bold]enter[/bold])'
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
            elif keypress in DefaultKeys.escape:
                return None
            elif keypress in DefaultKeys.confirm:
                if is_selected:
                    break
            elif keypress in DefaultKeys.tab:
                if is_selected:
                    current_message = yes_text if is_yes else no_text
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
