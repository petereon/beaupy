# More Examples

## `select`/`select_multiple`

### Functionality

#### Return index

Selective elements default to return the selected item (in case of `select`) or list of items (in case of `select_multiple`). This behavior can be modified by `return_index` parameter (or `return_indices` in case of the latter), see example,

```python
result_index = select(options=['I\'ll be returned as 0', 'I\'ll be returned as 1'],
                      return_index=True)
```

#### Starting cursor index

By default cursor is placed on the first element, this can be configured by `cursor_index` parameter as follows,

```python
results = select(['Not here either', 'Not here', 'Start from here'],
                 cursor_index=1)
```

#### Preticked indices for `select_multiple`

You can have preticked options using `ticked_indices` in `select_multiple`:

```python
loved_children = select_multiple(['Oldest child', 'Middle child', 'Youngest Child'],
                                 ticked_indices=[0,2])
```

#### Maximal and minimal count for `select_multiple`

With `select_multiple` you can restrict maximum and minimum count of elements using `maximal_count` and `minimal_count` respectively,

```python
pizza_toppings = select_multiple(['pineapple', 'olives', 'anchovies', 'mozzarella', 'parma ham']
                                 maximal_count=3,
                                 minimal_count=1)
```

### Styling

!!! tip
    For styling you can leverage [numerous styling options](https://rich.readthedocs.io/en/stable/style.html) provided by rich

#### Style as text

```python
stylish = select(options = ["red", "on", "white"],
                 cursor = "x",
                 cursor_style= "red on white")
```

#### Style as hex

```python
selections = select_multiple(options = ["s", "h", "e", "", "b", "e", "l", "i", "e", "v", "e", "d"],
                             tick_style="#af00ff",
                             ticked_indices=[1,2,6,7,8,11])
```

### Cursor characters

#### Emoji as a cursor

!!! bug
    Some emojis can appear as one character instead of two!

```python
result = select(options = ["here", "comes", "the", "sun"],
                cursor = "🌞")
```

#### Non-ascii as a cursor

```python
result = select(options = ["hardcore", "unicode"],
                cursor = "⇉")
```

#### Multi-character cursors/ticks

!!! tip
    You can use multiple characters as a cursor

```python
correct_abba_lyric = select_multiple(options = ["queen", "bean"],
                                     tick_character = "dancing")
```

## `prompt`

### Functionality

You can have a default prompt, which will collect the user typed response to the mood variable as string

```python
mood = prompt("How are you today?")
```

#### Validation

Additionally, you can validate the input using some sort of Callable `validator`, for example a lambda expression to make sure input is not numeric,

```python
answer = prompt(prompt="What is the answer to life the universe and everything?"
                validator=lambda val: not val.isnumeric())

```

#### Type Conversion

You might want to convert types for some sort of downstream functionality using `target_type`,

!!! note
    Validation is always second to type conversion

```python
number_between_1_and_10 = prompt("Give me a number between 1 and 10",
                                 target_type=int
                                 validator=lambda n: 0 < n <= 10)
```

#### Hidden/secure input

For sensitive input, `secure` flag can be utilized, replacing user entered input with `*`

```python
very_secret_info = prompt("Type you API key, hehe",
                          secure=True)
```

#### Completion

You can provide a python callable such as `Callable[[str], List[str]]` to provide completion options. String passed to the callable is the current user input.

```python
favorite_color = prompt("What is your favorite color?",
                        completion=lambda _: ["pink", "PINK", "P1NK"])
```

A more complex example with path completion:

```python
from os import listdir
from pathlib import Path

# ugly hacky path completion callable:
def path_completion(str_path: str = ""):
    if not str_path:
        return []
    try:
        path = Path(str_path)
        rest = ''
        if not path.exists():
            str_path, rest = str_path.rsplit('/', 1)
            path = Path(str_path or '/')

        filtered_list_dir = [i for i in listdir(path) if i.startswith(rest)]

        if not path.is_absolute():
            return ['./'+str(Path(path)/i) for i in filtered_list_dir]
        else:
            return [str(Path(path)/i) for i in filtered_list_dir]
    except Exception as e:
        return []

prompt(">", completion=path_completion)
```


## Spinners

### Styling

#### Spinner Animation

There are few built in spinner animations, namely: ARC, ARROWS, BARS, CLOCK, DIAMOND, DOT, DOTS, LINE, LOADING and MOON

Each of these can be used in a spinner:

```python
from beaupy.spinners import Spinner, ARC
spinner = Spinner(ARC, "Doing some heavy work")
spinner.start()
```

All that "animations" are, is but a list of string, so making your own is as trivial as this:

```python
from beaupy.spinners import Spinner
spinner = Spinner(['whee', 'whe ', 'wh  ', 'w   ', 'wh  ', 'whe ', 'whee'], "Whee!")
spinner.start()
```

#### Rich styling

Every text in spinner does accept and respect rich styles, so the following works:

```python
from beaupy.spinners import Spinner
spinner = Spinner(['[red]⬤[/red] ', '[green]⬤[/green] ', '[blue]⬤[/blue] '], '[pink1]Setting[/pink1] colors!')
spinner.start()
```

#### Animation speed

Animation speed can be set using `refresh_per_second` parameter:

```python
from beaupy.spinners import Spinner, LOADING
spinner = Spinner(LOADING, "something", refresh_per_second=4)
spinner.start()
```

## Global Configuration

`beaupy` exposes global configuration to configure behaviour of the CLI elements globally. There are currently 3 options:

- `raise_on_interrupt`: If `True`, functions will raise `KeyboardInterrupt` whenever one is encountered when waiting for input,
        otherwise, they will return some sane alternative to their usual return. For `select`, `prompt` and `confirm` this means `None`,
        while for `select_multiple` it means an empty list - `[]`. Defaults to `False`.
- `raise_on_escape`: If `True`, functions will raise `Abort` whenever the escape key is encountered when waiting for input, otherwise,
        they will return some sane alternative to their usual return. For `select`, `prompt` and `confirm` this means `None`, while for
        `select_multiple` it means an empty list - `[]`.  Defaults to `False`.
- `transient`: If `False`, elements will remain displayed after their context has ended. Defaults to `True`.

You can set these options like follows:

```python
from beaupy import Config

Config.raise_on_interrupt = True
Config.raise_on_escape = True
Config.transient = False
```

### Usage

For example, if you want to raise an exception when user presses `Ctrl+C` or `Esc` key, you can set `raise_on_interrupt` and `raise_on_escape` to `True`:

```python
from beaupy import Config, select

Config.raise_on_interrupt = True

try:
    result = select(['Option 1', 'Option 2'])
except KeyboardInterrupt:
    print("User pressed Ctrl+C")

print("Result:", result)
```