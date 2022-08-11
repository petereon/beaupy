#! /usr/bin/env python3
"""
Commandline User Tools for Input Easification
"""

__license__ = "MIT"

import getpass
from typing import List, Optional, Union
import sys

from rich.console import Console
import readchar

console = Console()
class DefaultKeys:
    """List of default keybindings.

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
    down: List[str] = [readchar.key.DOWN, "j"]
    up: List[str] = [readchar.key.UP, "k"]


def reset_line_up():
    sys.stdout.write("\x1b[2K\033[F\x1b[2K")


def get_number(
    prompt: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_float: bool = True,
) -> float:
    """Get a number from user input.
    If an invalid number is entered the user will be prompted again.

    Args:
        prompt (str): The prompt asking the user to input.
        min_value (float, optional): The [inclusive] minimum value.
        max_value (float, optional): The [inclusive] maximum value.
        allow_float (bool, optional): Allow floats or force integers.

    Returns:
        float: The number input by the user.
    """
    return_value: Optional[float] = None
    while return_value is None:
        input_value = input(prompt + " ")
        try:
            return_value = float(input_value)
        except ValueError:
            console.print("Not a valid number.\r", end="")
        if not allow_float and return_value is not None:
            if return_value != int(return_value):
                console.print("Has to be an integer.\r", end="")
                return_value = None
        if min_value is not None and return_value is not None:
            if return_value < min_value:
                console.print(f"Has to be at least {min_value}.\r", end="")
                return_value = None
        if max_value is not None and return_value is not None:
            if return_value > max_value:
                console.print(f"Has to be at most {max_value}.\r", end="")
                return_value = None
        if return_value is not None:
            break
    console.print("", end="")
    if allow_float:
        return return_value
    return int(return_value)


def secure_input(prompt: str) -> str:
    """Get secure input without showing it in the command line.

    Args:
        prompt (str): The prompt asking the user to input.

    Returns:
        str: The secure input.
    """
    return getpass.getpass(prompt + " ")


def select(
    options: List[str],
    cursor: str = "> ",
    cursor_color = 'pink1',
    selected_index: int = 0,
    strict: bool = False,
) -> Union[int, None]:
    if not options:
        if strict:
            raise ValueError('`options` cannot be empty')
        return None
    while True:
        format_option = lambda i, option: "{}{}".format(
            f'[{cursor_color}]{cursor}[/{cursor_color}]' if i == selected_index else ' ' * len(cursor), option
        )
        console.print("\n".join([format_option(i, option) for i, option in enumerate(options)]))

        for _ in range(len(options)):
            reset_line_up()
        keypress = readchar.readkey()
        if keypress in DefaultKeys.up:
            new_index = selected_index
            while new_index > 0:
                new_index -= 1
                selected_index = new_index
                break
        elif keypress in DefaultKeys.down:
            new_index = selected_index
            while new_index < len(options) - 1:
                new_index += 1
                selected_index = new_index
                break
        elif keypress in DefaultKeys.confirm:
            return selected_index
        elif keypress in DefaultKeys.interrupt:
            return None


def format_option(option, ticked, tick_character, tick_color, selected, selected_color):
    prefix = f"\[ ]"
    if ticked:
        prefix = f"\[[{tick_color}]{tick_character}[/{tick_color}]]"
    if selected:
        option = f"[{selected_color}]{option}[/{selected_color}]"
    return f"{prefix} {option}"


def select_multiple(
    options: List[str],
    tick_character: str = "x",
    tick_color: str = "cyan1",
    selected_color: str = "pink1",
    ticked_indices: Optional[List[int]] = None,
    cursor_index: int = 0,
    minimal_count: int = 0,
    maximal_count: Optional[int] = None,
) -> List[int]:

    if ticked_indices is None:
        ticked_indices = []
    max_index = len(options) - (1 if True else 0)
    error_message = ""
    while True:
        console.print(
            "\n".join(
                [
                    format_option(
                        option=option,
                        ticked=i in ticked_indices,
                        tick_character=tick_character,
                        tick_color=tick_color,
                        selected=i == cursor_index,
                        selected_color=selected_color,
                    )
                    for i, option in enumerate(options)
                ]
            )
        )
        for i in range(len(options)):
            reset_line_up()
        keypress = readchar.readkey()
        if keypress in DefaultKeys.up:
            new_index = cursor_index
            while new_index > 0:
                new_index -= 1
                cursor_index = new_index
                break
        elif keypress in DefaultKeys.down:
            new_index = cursor_index
            while new_index + 1 <= max_index:
                new_index += 1
                cursor_index = new_index
                break
        elif keypress in DefaultKeys.select:
            if cursor_index in ticked_indices:
                if len(ticked_indices) - 1 >= minimal_count:
                    ticked_indices.remove(cursor_index)
            elif maximal_count is not None:
                if len(ticked_indices) + 1 <= maximal_count:
                    ticked_indices.append(cursor_index)
            else:
                ticked_indices.append(cursor_index)
        elif keypress in DefaultKeys.confirm:
            if minimal_count > len(ticked_indices):
                error_message = f"Must select at least {minimal_count} options"
            elif maximal_count is not None and maximal_count < len(ticked_indices):
                error_message = f"Must select at most {maximal_count} options"
            else:
                break
        elif keypress in DefaultKeys.interrupt:
            raise KeyboardInterrupt
        if error_message != "":
            console.print(error_message)
    console.print("", end="")
    return ticked_indices


def prompt_yes_or_no(
    question: str,
    yes_text: str = "Yes",
    no_text: str = "No",
    has_to_match_case: bool = False,
    enter_empty_confirms: bool = True,
    default_is_yes: bool = False,
    deselected_prefix: str = "  ",
    selected_prefix: str = "[green]> [/green]",
    char_prompt: bool = True,
) -> Optional[bool]:
    """Prompt the user to input yes or no.

    Args:
        question (str): The prompt asking the user to input.
        yes_text (str, optional): The text corresponding to 'yes'.
        no_text (str, optional): The text corresponding to 'no'.
        has_to_match_case (bool, optional): Does the case have to match.
        enter_empty_confirms (bool, optional): Does enter on empty string work.
        default_is_yes (bool, optional): Is yes selected by default (no).
        deselected_prefix (str, optional): Prefix if something is deselected.
        selected_prefix (str, optional): Prefix if something is selected (> )
        char_prompt (bool, optional): Add a [Y/N] to the prompt.

    Returns:
        Optional[bool]: The bool what has been selected.
    """
    is_yes = default_is_yes
    is_selected = enter_empty_confirms
    current_message = ""
    yn_prompt = f" ({yes_text[0]}/{no_text[0]}) " if char_prompt else ": "
    while True:
        yes = is_yes and is_selected
        no = not is_yes and is_selected
        question_line = f"{question}{yn_prompt}{current_message}"
        console.print(
            f"{question_line}\n{selected_prefix if yes else deselected_prefix}{yes_text}\n{selected_prefix if no else deselected_prefix}{no_text}"
        )
        for _ in range(3):
            reset_line_up()
        keypress = readchar.readkey()
        if keypress in DefaultKeys.down or keypress in DefaultKeys.up:
            is_yes = not is_yes
            is_selected = True
            current_message = yes_text if is_yes else no_text
        elif keypress in DefaultKeys.delete:
            if current_message:
                current_message = current_message[:-1]
        elif keypress in DefaultKeys.interrupt:
            raise KeyboardInterrupt
        elif keypress in DefaultKeys.confirm:
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