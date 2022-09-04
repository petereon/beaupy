# Table of Contents

* [\_\_init\_\_](#__init__)
* [spinners](#spinners)
  * [Spinner](#spinners.Spinner)
    * [\_\_init\_\_](#spinners.Spinner.__init__)
    * [start](#spinners.Spinner.start)
    * [stop](#spinners.Spinner.stop)
* [\_internals](#_internals)
* [beaupy](#beaupy)
  * [DefaultKeys](#beaupy.DefaultKeys)
  * [Config](#beaupy.Config)
  * [prompt](#beaupy.prompt)
  * [select](#beaupy.select)
  * [select\_multiple](#beaupy.select_multiple)
  * [confirm](#beaupy.confirm)

<a id="__init__"></a>

# \_\_init\_\_

<a id="spinners"></a>

# spinners

<a id="spinners.Spinner"></a>

## Spinner Objects

```python
class Spinner()
```

<a id="spinners.Spinner.__init__"></a>

#### \_\_init\_\_

```python
def __init__(spinner_characters: List[str] = DOTS,
             text: str = 'Loading...',
             refresh_per_second: float = 10,
             transient: bool = True)
```

Creates a spinner which can be used to provide some user feedback during long processing

**Arguments**:

- `spinner_characters` _List[str]_ - List of characters that will be displayed in sequence by a spinner
- `text` _str_ - Static text that will be shown after the spinner. Defaults to `Loading...`
- `refresh_per_second` _float, optional_ - Number of refreshes the spinner will do a second, this will affect
  the fluidity of the "animation". Defaults to 10.
- `transient` _bool, optional_ - If the spinner will disappear after it's done, otherwise not. Defaults to True.
  

**Raises**:

- `ValueError` - Raised when no `spinner_characters` are provided in

<a id="spinners.Spinner.start"></a>

#### start

```python
def start() -> None
```

Starts the spinner

<a id="spinners.Spinner.stop"></a>

#### stop

```python
def stop() -> None
```

Stops the spinner

<a id="_internals"></a>

# \_internals

<a id="beaupy"></a>

# beaupy

A Python library of interactive CLI elements you have been looking for

<a id="beaupy.DefaultKeys"></a>

## DefaultKeys Objects

```python
class DefaultKeys()
```

A map of default keybindings.

**Attributes**:

- `interrupt(List[str])` - Keys that cause a keyboard interrupt.
- `select(List[str])` - Keys that trigger list element selection.
- `confirm(List[str])` - Keys that trigger list confirmation.
- `delete(List[str])` - Keys that trigger character deletion.
- `down(List[str])` - Keys that select the element below.
- `up(List[str])` - Keys that select the element above.

<a id="beaupy.Config"></a>

## Config Objects

```python
class Config()
```

A map of default configuration

**Attributes**:

- `raise_on_interrupt(bool)` - If True, functions will raise KeyboardInterrupt whenever one is encountered when waiting for input,
  otherwise, they will return some sane alternative to their usual return (e.g.: None, [] ). Defaults to False.

<a id="beaupy.prompt"></a>

#### prompt

```python
def prompt(prompt: str,
           target_type: Type[TargetType] = str,
           validator: Callable[[TargetType], bool] = lambda input: True,
           secure: bool = False,
           raise_validation_fail: bool = True,
           raise_type_conversion_fail: bool = True) -> TargetType
```

Function that prompts the user for written input

**Arguments**:

- `prompt` _str_ - The prompt that will be displayed
- `target_type` _Union[Type[T], Type[str]], optional_ - Type to convert the answer to. Defaults to str.
- `validator` _Callable[[Any], bool], optional_ - Optional function to validate the input. Defaults to lambda input: True.
- `secure` _bool, optional_ - If True, input will be hidden. Defaults to False.
- `raise_validation_fail` _bool, optional_ - If True, invalid inputs will raise `rich.internals.ValidationError`, else
  the error will be reported onto the console. Defaults to True.
- `raise_type_conversion_fail` _bool, optional_ - If True, invalid inputs will raise `rich.internals.ConversionError`, else
  the error will be reported onto the console. Defaults to True.
  

**Raises**:

- `ValidationError` - Raised if validation with provided validator fails
- `ConversionError` - Raised if the value cannot be converted to provided type
- `KeyboardInterrupt` - Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True
  

**Returns**:

  Union[T, str]: Returns a value formatted as provided type or string if no type is provided

<a id="beaupy.select"></a>

#### select

```python
def select(options: List[Any],
           preprocessor: Callable[[Any], Any] = lambda val: val,
           cursor: str = '>',
           cursor_style: str = 'pink1',
           cursor_index: int = 0,
           return_index: bool = False,
           strict: bool = False) -> Union[Selection, None]
```

A prompt that allows selecting one option from a list of options

**Arguments**:

- `options` _List[Any]_ - A list of options to select from
- `preprocessor` _Callable[[Any], Any]_ - A callable that can be used to preprocess the list of options prior to printing.
  For example, if you passed a `Person` object with `name` attribute, preprocessor
  could be `lambda person: person.name` to just show the content of `name` attribute
  in the select dialog. Defaults to `lambda val: val`
- `cursor` _str, optional_ - Cursor that is going to appear in front of currently selected option. Defaults to '> '.
- `cursor_style` _str, optional_ - Rich friendly style for the cursor. Defaults to 'pink1'.
- `cursor_index` _int, optional_ - Option can be preselected based on its list index. Defaults to 0.
- `return_index` _bool, optional_ - If `True`, `select` will return the index of selected element in options. Defaults to `False`.
- `strict` _bool, optional_ - If empty `options` is provided and strict is `False`, None will be returned,
  if it's `True`, `ValueError` will be thrown. Defaults to False.
  

**Raises**:

- `ValueError` - Thrown if no `options` are povided and strict is `True`
- `KeyboardInterrupt` - Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True
  

**Returns**:

  Union[int, str, None]: Selected value or the index of a selected option or `None`

<a id="beaupy.select_multiple"></a>

#### select\_multiple

```python
def select_multiple(options: List[Any],
                    preprocessor: Callable[[Any], Any] = lambda val: val,
                    tick_character: str = '✓',
                    tick_style: str = 'pink1',
                    cursor_style: str = 'pink1',
                    ticked_indices: Optional[List[int]] = None,
                    cursor_index: int = 0,
                    minimal_count: int = 0,
                    maximal_count: Optional[int] = None,
                    return_indices: bool = False,
                    strict: bool = False) -> Selections
```

A prompt that allows selecting multiple options from a list of options

**Arguments**:

- `options` _List[Any]_ - A list of options to select from
- `preprocessor` _Callable[[Any], Any]_ - A callable that can be used to preprocess the list of options prior to printing.
  For example, if you passed a `Person` object with `name` attribute, preprocessor
  could be `lambda person: person.name` to just show the content of `name` attribute
  in the select dialog. Defaults to `lambda val: val`
- `tick_character` _str, optional_ - Character that will be used as a tick in a checkbox. Defaults to 'x'.
- `tick_style` _str, optional_ - Rich friendly style for the tick character. Defaults to 'pink1'.
- `cursor_style` _str, optional_ - Rich friendly style for the option when the cursor is currently on it. Defaults to 'pink1'.
- `ticked_indices` _Optional[List[int]], optional_ - Indices of options that are pre-ticked when the prompt appears. Defaults to None.
- `cursor_index` _int, optional_ - Index of the option cursor starts at. Defaults to 0.
- `minimal_count` _int, optional_ - Minimal count of options that need to be selected. Defaults to 0.
- `maximal_count` _Optional[int], optional_ - Maximal count of options that need to be selected. Defaults to None.
- `return_indices` _bool, optional_ - If `True`, `select_multiple` will return the indices
  of ticked elements in options. Defaults to `False`.
- `strict` _bool, optional_ - If empty `options` is provided and strict is `False`, None will be returned,
  if it's `True`, `ValueError` will be thrown. Defaults to False.
  

**Raises**:

- `KeyboardInterrupt` - Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True
  

**Returns**:

  Union[List[str], List[int]]: A list of selected values or indices of selected options

<a id="beaupy.confirm"></a>

#### confirm

```python
def confirm(question: str,
            yes_text: str = 'Yes',
            no_text: str = 'No',
            has_to_match_case: bool = False,
            enter_empty_confirms: bool = True,
            default_is_yes: bool = False,
            cursor: str = '>',
            cursor_style: str = 'pink1',
            char_prompt: bool = True) -> Optional[bool]
```

A prompt that asks a question and offers two responses

**Arguments**:

- `question` _str_ - Question to be asked
- `yes_text` _str, optional_ - Text of the positive response. Defaults to 'Yes'.
- `no_text` _str, optional_ - Text of the negative response. Defaults to 'No'.
- `has_to_match_case` _bool, optional_ - Check if typed response matches case. Defaults to False.
- `enter_empty_confirms` _bool, optional_ - No response is confirmation. Defaults to True.
- `default_is_yes` _bool, optional_ - Default is Yes. Defaults to False.
- `cursor` _str, optional_ - What character(s) to use as a cursor. Defaults to '> '.
- `cursor_style` _str, optional_ - Rich friendly style for the cursor. Defaults to 'pink1'.
- `char_prompt` _bool, optional_ - Print [Y/n] after the question. Defaults to True.
  

**Raises**:

- `KeyboardInterrupt` - Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True
  

**Returns**:

  Optional[bool]

