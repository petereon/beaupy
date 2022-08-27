#! /usr/bin/env python3
"""
A Python library of interactive CLI elements you have been looking for
"""

__license__ = "MIT"

import ast
import logging
import warnings
from typing import Any, Callable, List, Optional, Type, Union

import readchar
from rich.console import Console

from beaupy.internals import (
    ConversionError,
    ValidationError,
    format_option_select,
    format_option_select_multiple,
    render,
    reset_lines,
)

console = Console()


class DefaultKeys:
    """A map of default keybindings.

    Attributes:
        interrupt(List[str]): Keys that cause a keyboard interrupt.
        select(List[str]): Keys that trigger list element selection.
        confirm(List[str]): Keys that trigger list confirmation.
        delete(List[str]): Keys that trigger character deletion.
        down(List[str]): Keys that select the element below.
        up(List[str]): Keys that select the element above.
    """

    interrupt: List[str] = [readchar.key.CTRL_C, readchar.key.CTRL_D]
    select: List[str] = [readchar.key.SPACE]
    confirm: List[str] = [readchar.key.ENTER]
    delete: List[str] = [readchar.key.BACKSPACE]
    down: List[str] = [readchar.key.DOWN]
    up: List[str] = [readchar.key.UP]


class Config:
    """A map of default configuration

    Attributes:
        raise_on_interrupt(bool): If True, functions will raise KeyboardInterrupt whenever one is encountered when waiting for input,
        otherwise, they will return some sane alternative to their usual return (e.g.: None, [] ). Defaults to False.
    """

    raise_on_interrupt: bool = False
    default_keys = DefaultKeys


def prompt(
    prompt: str,
    target_type: Type = str,
    validator: Callable[[Any], bool] = lambda input: True,
    secure: bool = False,
) -> Any:
    """Function that prompts the user for written input

    Args:
        prompt (str): The prompt that will be displayed
        target_type (Union[Type[T], Type[str]], optional): Type to convert the answer to. Defaults to str.
        validator (Callable[[Any], bool], optional): Optional function to validate the input. Defaults to lambdainput:True.
        secure (bool, optional): If True, input will be hidden. Defaults to False.

    Raises:
        ValidationError: Raised if validation with provided validator fails
        ConversionError: Raised if the value cannot be converted to provided type
        KeyboardInterrupt: Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True

    Returns:
        Union[T, str]: Returns a value formatted as provided type or string if no type is provided
    """
    value: str = ""
    render(secure, "", prompt, console)
    while True:
        char = readchar.readkey()
        if char in Config.default_keys.confirm:
            try:
                if target_type is bool:
                    result: bool = ast.literal_eval(value)
                    if not isinstance(result, bool):
                        raise ValueError()
                else:
                    result: target_type = target_type(value)  # type: ignore

                if validator(result):
                    return result
                else:
                    raise ValidationError(f"`{'secure input' if secure else value}` cannot be validated")
            except ValueError:
                raise ConversionError(f"`{'secure input' if secure else value}` cannot be converted to type `{target_type}`") from None
        elif char in Config.default_keys.delete:
            value = value[:-1]
            render(secure, value, prompt, console)
        elif char in Config.default_keys.interrupt:
            if Config.raise_on_interrupt:
                raise KeyboardInterrupt()
            else:
                return None
        else:
            value += char
            render(secure, value, prompt, console)


def select(
    options: List[str],
    cursor: str = ">",
    cursor_style: str = "pink1",
    cursor_index: int = 0,
    return_index: bool = False,
    strict: bool = False,
) -> Union[int, str, None]:
    """A prompt that allows selecting one option from a list of options

    Args:
        options (List[str]): A list of options to select from
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
    if not options:
        if strict:
            raise ValueError("`options` cannot be empty")
        return None
    if cursor_style in ["", None]:
        logging.warning("`cursor_style` should be a valid style, defaulting to `white`")
        cursor_style = "white"
    while True:
        console.print("\n".join([format_option_select(i, cursor_index, option, cursor_style, cursor) for i, option in enumerate(options)]))

        reset_lines(len(options))
        keypress = readchar.readkey()
        if keypress in Config.default_keys.up:
            new_index = cursor_index
            if new_index > 0:
                new_index -= 1
                cursor_index = new_index
        elif keypress in Config.default_keys.down:
            new_index = cursor_index
            if new_index < len(options) - 1:
                new_index += 1
                cursor_index = new_index
        elif keypress in Config.default_keys.confirm:
            if return_index:
                return cursor_index
            return options[cursor_index]
        elif keypress in Config.default_keys.interrupt:
            if Config.raise_on_interrupt:
                raise KeyboardInterrupt
            return None


def select_multiple(
    options: List[str],
    tick_character: str = "✓",
    tick_style: str = "pink1",
    cursor_style: str = "pink1",
    ticked_indices: Optional[List[int]] = None,
    cursor_index: int = 0,
    minimal_count: int = 0,
    maximal_count: Optional[int] = None,
    return_indices: bool = False,
    strict: bool = False,
) -> Union[List[str], List[int]]:
    """A prompt that allows selecting multiple options from a list of options

    Args:
        options (List[str]): A list of options to select from
        tick_character (str, optional): Character that will be used as a tick in a checkbox. Defaults to 'x'.
        tick_style (str, optional): Rich friendly style for the tick character. Defaults to 'pink1'.
        cursor_style (str, optional): Rich friendly style for the option when the cursor is currently on it. Defaults to 'pink1'.
        ticked_indices (Optional[List[int]], optional): Indices of options that are pre-ticked when the prompt appears. Defaults to None.
        cursor_index (int, optional): Index of the option cursor starts at. Defaults to 0.
        minimal_count (int, optional): Minimal count of options that need to be selected. Defaults to 0.
        maximal_count (Optional[int], optional): Maximal count of options that need to be selected. Defaults to None.
        return_indices (bool, optional): If `True`, `select_multiple` will return the indices of ticked elements in options. Defaults to `False`.
        strict (bool, optional): If empty `options` is provided and strict is `False`, None will be returned, if it's `True`, `ValueError` will be thrown. Defaults to False.

    Raises:
        KeyboardInterrupt: Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True

    Returns:
        Union[List[str], List[int]]: A list of selected values or indices of selected options
    """
    if not options:
        if strict:
            raise ValueError("`options` cannot be empty")
        return []  # type: ignore
    if cursor_style in ["", None]:
        logging.warning("`cursor_style` should be a valid style, defaulting to `white`")
        cursor_style = "white"
    if tick_style in ["", None]:
        logging.warning("`tick_style` should be a valid style, defaulting to `white`")
        tick_style = "white"
    if ticked_indices is None:
        ticked_indices = []
    max_index = len(options) - (1 if True else 0)
    error_message = ""
    while True:
        console.print(
            "\n".join(
                [
                    format_option_select_multiple(
                        option=option,
                        ticked=i in ticked_indices,
                        tick_character=tick_character,
                        tick_style=tick_style,
                        selected=i == cursor_index,
                        cursor_style=cursor_style,
                    )
                    for i, option in enumerate(options)
                ]
            )
        )
        reset_lines(len(options))
        keypress = readchar.readkey()
        if keypress in Config.default_keys.up:
            new_index = cursor_index
            if new_index > 0:
                new_index -= 1
                cursor_index = new_index
        elif keypress in Config.default_keys.down:
            new_index = cursor_index
            if new_index + 1 <= max_index:
                new_index += 1
                cursor_index = new_index
        elif keypress in Config.default_keys.select:
            if cursor_index in ticked_indices:
                if len(ticked_indices) - 1 >= minimal_count:
                    ticked_indices.remove(cursor_index)
            elif maximal_count is not None:
                if len(ticked_indices) + 1 <= maximal_count:
                    ticked_indices.append(cursor_index)
            else:
                ticked_indices.append(cursor_index)
        elif keypress in Config.default_keys.confirm:
            if minimal_count > len(ticked_indices):
                error_message = f"Must select at least {minimal_count} options"
            elif maximal_count is not None and maximal_count < len(ticked_indices):
                error_message = f"Must select at most {maximal_count} options"
            else:
                break
        elif keypress in Config.default_keys.interrupt:
            if Config.raise_on_interrupt:
                raise KeyboardInterrupt
            return []  # type: ignore
        if error_message != "":
            console.print(error_message)
            error_message = ""
    if return_indices:
        return ticked_indices
    return [options[i] for i in ticked_indices]


def confirm(
    question: str,
    yes_text: str = "Yes",
    no_text: str = "No",
    has_to_match_case: bool = False,
    enter_empty_confirms: bool = True,
    default_is_yes: bool = False,
    cursor: str = "> ",
    cursor_style: str = "pink1",
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
    if cursor_style in ["", None]:
        logging.warning("`cursor_style` should be a valid style, defaulting to `white`")
        cursor_style = "white"
    is_yes = default_is_yes
    is_selected = enter_empty_confirms
    current_message = ""
    yn_prompt = f" ({yes_text[0]}/{no_text[0]}) " if char_prompt else ": "
    selected_prefix = f"[{cursor_style}]{cursor}[/{cursor_style}]"
    deselected_prefix = " " * len(cursor)
    while True:
        yes = is_yes and is_selected
        no = not is_yes and is_selected
        question_line = f"{question}{yn_prompt}{current_message}"
        console.print(
            f"{question_line}\n{selected_prefix if yes else deselected_prefix}{yes_text}\n{selected_prefix if no else deselected_prefix}{no_text}"
        )
        reset_lines(3)
        keypress = readchar.readkey()
        if keypress in Config.default_keys.down or keypress in Config.default_keys.up:
            is_yes = not is_yes
            is_selected = True
            current_message = yes_text if is_yes else no_text
        elif keypress in Config.default_keys.delete:
            if current_message:
                current_message = current_message[:-1]
        elif keypress in Config.default_keys.interrupt:
            if Config.raise_on_interrupt:
                raise KeyboardInterrupt
            return None
        elif keypress in Config.default_keys.confirm:
            if is_selected:
                break
        elif keypress in "\t":
            if is_selected:
                current_message = yes_text if is_yes else no_text
        else:
            current_message += keypress
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


# TODO: Add filter function that will allow for list of options and text based filter
