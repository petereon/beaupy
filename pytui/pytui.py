#! /usr/bin/env python3
'''
Commandline User Tools for Input Easification
'''

__license__ = 'MIT'

import getpass
import sys
from typing import Callable, List, Optional, Type, TypeVar, Union

import readchar
from rich.console import Console

console = Console()


class DefaultKeys:
    '''List of default keybindings.

    Attributes:
        interrupt(List[str]): Keys that cause a keyboard interrupt.
        select(List[str]): Keys that trigger list element selection.
        confirm(List[str]): Keys that trigger list confirmation.
        delete(List[str]): Keys that trigger character deletion.
        down(List[str]): Keys that select the element below.
        up(List[str]): Keys that select the element above.
    '''

    interrupt: List[str] = [readchar.key.CTRL_C, readchar.key.CTRL_D]
    select: List[str] = [readchar.key.SPACE]
    confirm: List[str] = [readchar.key.ENTER]
    delete: List[str] = [readchar.key.BACKSPACE]
    down: List[str] = [readchar.key.DOWN, 'j']
    up: List[str] = [readchar.key.UP, 'k']


def reset_line_up():
    sys.stdout.write('\x1b[2K\033[F\x1b[2K')

# TODO: rewrite `prompt_number` and `prompt_secure` into just `prompt` and offering a parameter that takes type to validate against
# and another parameter for secure/plaintext input

T = TypeVar('T')

def prompt(
    prompt: str,
    type: Type[T] = str,
    validator: Callable = lambda input: True
) -> Union[T, str]:
    pass

def prompt_number(
    prompt: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_float: bool = True,
) -> float:
    '''Get a number from user input.
    If an invalid number is entered the user will be prompted again.

    Args:
        prompt (str): The prompt asking the user to input.
        min_value (float, optional): The [inclusive] minimum value.
        max_value (float, optional): The [inclusive] maximum value.
        allow_float (bool, optional): Allow floats or force integers.

    Returns:
        float: The number input by the user.
    '''
    return_value: Optional[float] = None
    while return_value is None:
        input_value = input(prompt + ' ')
        try:
            return_value = float(input_value)
        except ValueError:
            console.print('Not a valid number.\r', end='')
        if not allow_float and return_value is not None:
            if return_value != int(return_value):
                console.print('Has to be an integer.\r', end='')
                return_value = None
        if min_value is not None and return_value is not None:
            if return_value < min_value:
                console.print(f'Has to be at least {min_value}.\r', end='')
                return_value = None
        if max_value is not None and return_value is not None:
            if return_value > max_value:
                console.print(f'Has to be at most {max_value}.\r', end='')
                return_value = None
        if return_value is not None:
            break
    console.print('', end='')
    if allow_float:
        return return_value
    return int(return_value)


def prompt_secure(prompt: str) -> str:
    '''Get secure input without showing it in the command line.

    Args:
        prompt (str): The prompt asking the user to input.

    Returns:
        str: The secure input.
    '''
    return getpass.getpass(prompt + ' ')


def select(
    options: List[str],
    cursor: str = '> ',
    cursor_color='pink1',
    cursor_index: int = 0,
    strict: bool = False,
) -> Union[int, None]:
    '''A prompt that allows selecting one option from a list of options

    Args:
        options (List[str]): A list of options to select from
        cursor (str, optional): Cursor that is going to appear in front of currently selected option. Defaults to '> '.
        cursor_color (str, optional): Color of the cursor. Defaults to 'pink1'.
        cursor_index (int, optional): Option can be preselected based on its list index. Defaults to 0.
        strict (bool, optional): If empty `options` is provided and strict is `False`, None will be returned, if it's `True`, `ValueError` will be thrown. Defaults to False.

    Raises:
        ValueError: Thrown if no `options` are povided and strict is `True`

    Returns:
        Union[int, None]: Index of a selected option or `None`
    '''
    if not options:
        if strict:
            raise ValueError('`options` cannot be empty')
        return None
    while True:
        format_option = lambda i, option: '{}{}'.format(
            f'[{cursor_color}]{cursor}[/{cursor_color}]'
            if i == cursor_index else ' ' * len(cursor),
            option,
        )
        console.print('\n'.join(
            [format_option(i, option) for i, option in enumerate(options)]))

        for _ in range(len(options)):
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
            while new_index < len(options) - 1:
                new_index += 1
                cursor_index = new_index
                break
        elif keypress in DefaultKeys.confirm:
            return cursor_index
        elif keypress in DefaultKeys.interrupt:
            return None


def format_option(option, ticked, tick_character, tick_color, selected,
                  selected_color):
    prefix = f'\[ ]'
    if ticked:
        prefix = f'\[[{tick_color}]{tick_character}[/{tick_color}]]'
    if selected:
        option = f'[{selected_color}]{option}[/{selected_color}]'
    return f'{prefix} {option}'


def select_multiple(
    options: List[str],
    tick_character: str = 'x',
    tick_color: str = 'cyan1',
    cursor_color: str = 'pink1',
    ticked_indices: Optional[List[int]] = None,
    cursor_index: int = 0,
    minimal_count: int = 0,
    maximal_count: Optional[int] = None,
    strict: bool = False, 
) -> List[int]:
    '''A prompt that allows selecting multiple options from a list of options

    Args:
        options (List[str]): A list of options to select from
        tick_character (str, optional): Character that will be used as a tick in a checkbox. Defaults to 'x'.
        tick_color (str, optional): Color of the tick character. Defaults to 'cyan1'.
        cursor_color (str, optional): Color of the option when the cursor is currently on it. Defaults to 'pink1'.
        ticked_indices (Optional[List[int]], optional): Indices of options that are pre-ticked when the prompt appears. Defaults to None.
        cursor_index (int, optional): Index of the option cursor starts at. Defaults to 0.
        minimal_count (int, optional): Minimal count of options that need to be selected. Defaults to 0.
        maximal_count (Optional[int], optional): Maximal count of options that need to be selected. Defaults to None.
        strict (bool, optional): If empty `options` is provided and strict is `False`, None will be returned, if it's `True`, `ValueError` will be thrown. Defaults to False.

    Raises:
        KeyboardInterrupt: Raised when Ctrl+C is encountered

    Returns:
        List[int]: A list of selected indices
    '''
    if not options:
        if strict:
            raise ValueError('`options` cannot be empty')
        return []
    if ticked_indices is None:
        ticked_indices = []
    max_index = len(options) - (1 if True else 0)
    error_message = ''
    while True:
        console.print('\n'.join([
            format_option(
                option=option,
                ticked=i in ticked_indices,
                tick_character=tick_character,
                tick_color=tick_color,
                selected=i == cursor_index,
                selected_color=cursor_color,
            ) for i, option in enumerate(options)
        ]))
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
                error_message = f'Must select at least {minimal_count} options'
            elif maximal_count is not None and maximal_count < len(
                    ticked_indices):
                error_message = f'Must select at most {maximal_count} options'
            else:
                break
        elif keypress in DefaultKeys.interrupt:
            raise KeyboardInterrupt
        if error_message != '':
            console.print(error_message)
            error_message = ''
    return ticked_indices


def confirm(
    question: str,
    yes_text: str = 'Yes',
    no_text: str = 'No',
    has_to_match_case: bool = False,
    enter_empty_confirms: bool = True,
    default_is_yes: bool = False,
    cursor: str = '> ',
    cursor_color: str = 'magenta1',
    char_prompt: bool = True,
) -> Optional[bool]:
    '''A prompt that asks a question and offers two responses

    Args:
        question (str): Question to be asked
        yes_text (str, optional): Text of the positive response. Defaults to 'Yes'.
        no_text (str, optional): Text of the negative response. Defaults to 'No'.
        has_to_match_case (bool, optional): Check if typed response matches case. Defaults to False.
        enter_empty_confirms (bool, optional): No response is confirmation. Defaults to True.
        default_is_yes (bool, optional): Default is Yes. Defaults to False.
        cursor (str, optional): What character(s) to use as a cursor. Defaults to '> '.
        cursor_color (str, optional): Color of the cursor. Defaults to 'magenta1'.
        char_prompt (bool, optional): Print [Y/n] after the question. Defaults to True.

    Raises:
        KeyboardInterrupt: Raised when Ctrl+C is encountered

    Returns:
        Optional[bool]
    '''
    is_yes = default_is_yes
    is_selected = enter_empty_confirms
    current_message = ''
    yn_prompt = f' ({yes_text[0]}/{no_text[0]}) ' if char_prompt else ': '
    selected_prefix = f'[{cursor_color}]{cursor}[/{cursor_color}]'
    deselected_prefix = ' ' * len(cursor)
    while True:
        yes = is_yes and is_selected
        no = not is_yes and is_selected
        question_line = f'{question}{yn_prompt}{current_message}'
        console.print(
            f'{question_line}\n{selected_prefix if yes else deselected_prefix}{yes_text}\n{selected_prefix if no else deselected_prefix}{no_text}'
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
        elif keypress in '\t':
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
