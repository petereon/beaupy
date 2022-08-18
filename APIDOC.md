<a id="__init__"></a>

# \_\_init\_\_

<a id="beaupy"></a>

# beaupy

Commandline User Tools for Input Easification

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
           target_type: Union[Type[T], Type[str]] = str,
           validator: Callable[[Any], bool] = lambda input: True,
           secure: bool = False) -> Union[T, str]
```

Function that prompts the user for written input

**Arguments**:

- `prompt` _str_ - The prompt that will be displayed
- `target_type` _Union[Type[T], Type[str]], optional_ - Type to convert the answer to. Defaults to str.
- `validator` _Callable[[Any], bool], optional_ - Optional function to validate the input. Defaults to lambdainput:True.
- `secure` _bool, optional_ - If True, input will be hidden. Defaults to False.
  

**Raises**:

- `ValidationError` - Raised if validation with provided validator fails
- `ConversionError` - Raised if the value cannot be converted to provided type
- `KeyboardInterrupt` - Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True
  

**Returns**:

  Union[T, str]: Returns a value formatted as provided type or string if no type is provided

<a id="beaupy.select"></a>

#### select

```python
def select(options: List[str],
           cursor: str = "> ",
           cursor_style="pink1",
           cursor_index: int = 0,
           strict: bool = False) -> Union[int, None]
```

A prompt that allows selecting one option from a list of options

**Arguments**:

- `options` _List[str]_ - A list of options to select from
- `cursor` _str, optional_ - Cursor that is going to appear in front of currently selected option. Defaults to '> '.
- `cursor_style` _str, optional_ - Rich friendly style for the cursor. Defaults to 'pink1'.
- `cursor_index` _int, optional_ - Option can be preselected based on its list index. Defaults to 0.
- `strict` _bool, optional_ - If empty `options` is provided and strict is `False`, None will be returned, if it's `True`, `ValueError` will be thrown. Defaults to False.
  

**Raises**:

- `ValueError` - Thrown if no `options` are povided and strict is `True`
- `KeyboardInterrupt` - Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True
  

**Returns**:

  Union[int, None]: Index of a selected option or `None`

<a id="beaupy.select_multiple"></a>

#### select\_multiple

```python
def select_multiple(options: List[str],
                    tick_character: str = "✓",
                    tick_style: str = "pink1",
                    cursor_style: str = "pink1",
                    ticked_indices: Optional[List[int]] = None,
                    cursor_index: int = 0,
                    minimal_count: int = 0,
                    maximal_count: Optional[int] = None,
                    strict: bool = False) -> List[int]
```

A prompt that allows selecting multiple options from a list of options

**Arguments**:

- `options` _List[str]_ - A list of options to select from
- `tick_character` _str, optional_ - Character that will be used as a tick in a checkbox. Defaults to 'x'.
- `tick_style` _str, optional_ - Rich friendly style for the tick character. Defaults to 'pink1'.
- `cursor_style` _str, optional_ - Rich friendly style for the option when the cursor is currently on it. Defaults to 'pink1'.
- `ticked_indices` _Optional[List[int]], optional_ - Indices of options that are pre-ticked when the prompt appears. Defaults to None.
- `cursor_index` _int, optional_ - Index of the option cursor starts at. Defaults to 0.
- `minimal_count` _int, optional_ - Minimal count of options that need to be selected. Defaults to 0.
- `maximal_count` _Optional[int], optional_ - Maximal count of options that need to be selected. Defaults to None.
- `strict` _bool, optional_ - If empty `options` is provided and strict is `False`, None will be returned, if it's `True`, `ValueError` will be thrown. Defaults to False.
  

**Raises**:

- `KeyboardInterrupt` - Raised when keyboard interrupt is encountered and Config.raise_on_interrupt is True
  

**Returns**:

- `List[int]` - A list of selected indices

<a id="beaupy.confirm"></a>

#### confirm

```python
def confirm(question: str,
            yes_text: str = "Yes",
            no_text: str = "No",
            has_to_match_case: bool = False,
            enter_empty_confirms: bool = True,
            default_is_yes: bool = False,
            cursor: str = "> ",
            cursor_style: str = "pink1",
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

