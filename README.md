# PyTUI

> :star: A library of interactive CLI elements you have been looking for :keyboard:

**PyTUI** implements a number of common interactive elements:

| Function                       | Functionality                                        |
|:-------------------------------|:-----------------------------------------------------|
| `select`                       | Prompt to pick a choice from a list                  |
| `select_multiple` (checkboxes) | Prompt to select one or multiple choices from a list |
| `confirm`                      | Prompt with a question and yes/no options            |
| `prompt_secure`                |           Prompt that takes input without displaying |
| `prompt_number`                | Prompt that takes a numeric input and validates      |

## Usage

![example](./example.gif)


```python
import pytui


def main():
    """Main."""
    if pytui.confirm("Are you brave enough to continue?"):
        names = [
            "Arthur, King of the Britons",
            "Sir Lancelot the Brave",
            "Sir Robin the Not-Quite-So-Brave-as-Sir-Lancelot",
            "Sir Bedevere the Wise",
            "Sir Galahad the Pure",
        ]

        name = names[pytui.select(names, cursor_index=3)]
        print(f"Welcome, {name}")
        # Get an integer greater or equal to 0
        age = pytui.prompt("What is your age?", type=int, validator=lambda val: val > 0)
        nemeses_options = [
            "The French",
            "The Police",
            "The Knights Who Say Ni",
            "Women",
            "The Black Knight",
            "The Bridge Keeper",
            "The Rabbit of Caerbannog",
        ]
        print("Choose your nemeses")
        # Choose multiple options from a list
        nemeses_indices = pytui.select_multiple(nemeses_options)
        nemeses = [
            nemesis
            for nemesis_index, nemesis in enumerate(nemeses_options)
            if nemesis_index in nemeses_indices
        ]
        # Get input without showing it being typed
        quest = pytui.prompt("What is your quest?", secure=True)
        print(f"{name}'s quest (who is {age}) is {quest}.")
        if nemeses:
            if len(nemeses) == 1:
                print(f"His nemesis is {nemeses[0]}.")
            else:
                print(f'His nemeses are {" and ".join(nemeses)}.')
        else:
            print("He has no nemesis.")

```

## Installation

> :warning: No PyPI release is available yet

From source:
```sh
git clone https://github.com/petereon/pytui.git
poetry build
pip install ./dist/pytui-{{some-version}}-py3-none-any.whl
```

## Roadmap

1. Achieve >90% test coverage
2. PyPI Release
3. Extend `select` with filterability
4. ...

## Docmentation

**PyTUI** is a library of interactive TUI elements for CLI applications. It is based on another library built for the same purpose, [`cutie`](https://github.com/kamik423/cutie).

In comparison, **PyTUI** is

- more [rich](https://rich.readthedocs.io/en/stable/) friendly
- more opinionated
- less unicode heavy (relies on [rich](https://rich.readthedocs.io/en/stable/) for this)

### API Doc
<a id="pytui.prompt"></a>

#### prompt

```python
def prompt(prompt: str,
           type: Union[Type[T], Type[str]] = str,
           validator: Callable[[Any], bool] = lambda input: True,
           secure: bool = False) -> Union[T, str]
```

Function that prompts the user for written input

**Arguments**:

- `prompt` _str_ - The prompt that will be displayed
- `type` _Union[Type[T], Type[str]], optional_ - Type to convert the answer to. Defaults to str.
- `validator` _Callable[[Any], bool], optional_ - Optional function to validate the input. Defaults to lambdainput:True.
- `secure` _bool, optional_ - If True, input will be hidden. Defaults to False.
  

**Raises**:

- `ValidationError` - Raised if validation with provided validator fails
- `ConversionError` - Raised if the value cannot be converted to provided type
- `KeyboardInterrupt` - Raised when keyboard interrupt is encountered
  

**Returns**:

  Union[T, str]: Returns a value formatted as provided type or string if no type is provided

<a id="pytui.select"></a>

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
  

**Returns**:

  Union[int, None]: Index of a selected option or `None`

<a id="pytui.select_multiple"></a>

#### select\_multiple

```python
def select_multiple(options: List[str],
                    tick_character: str = "x",
                    tick_style: str = "cyan1",
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
- `tick_style` _str, optional_ - Rich friendly style for the tick character. Defaults to 'cyan1'.
- `cursor_style` _str, optional_ - Rich friendly style for the option when the cursor is currently on it. Defaults to 'pink1'.
- `ticked_indices` _Optional[List[int]], optional_ - Indices of options that are pre-ticked when the prompt appears. Defaults to None.
- `cursor_index` _int, optional_ - Index of the option cursor starts at. Defaults to 0.
- `minimal_count` _int, optional_ - Minimal count of options that need to be selected. Defaults to 0.
- `maximal_count` _Optional[int], optional_ - Maximal count of options that need to be selected. Defaults to None.
- `strict` _bool, optional_ - If empty `options` is provided and strict is `False`, None will be returned, if it's `True`, `ValueError` will be thrown. Defaults to False.
  

**Raises**:

- `KeyboardInterrupt` - Raised when Ctrl+C is encountered
  

**Returns**:

- `List[int]` - A list of selected indices

<a id="pytui.confirm"></a>

#### confirm

```python
def confirm(question: str,
            yes_text: str = "Yes",
            no_text: str = "No",
            has_to_match_case: bool = False,
            enter_empty_confirms: bool = True,
            default_is_yes: bool = False,
            cursor: str = "> ",
            cursor_style: str = "magenta1",
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
- `cursor_style` _str, optional_ - Rich friendly style for the cursor. Defaults to 'magenta1'.
- `char_prompt` _bool, optional_ - Print [Y/n] after the question. Defaults to True.
  

**Raises**:

- `KeyboardInterrupt` - Raised when Ctrl+C is encountered
  

**Returns**:

  Optional[bool]


## Contributing

If you want to contribute, please feel free to suggest features or implement them yourself.

Also **please report any issues and bugs you might find!**

## License

The project is licensed under the [MIT-License](LICENSE).
