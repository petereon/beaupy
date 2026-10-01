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

Everything after the first argument (the animation) is keyword-only. A spinner can be driven by hand with `start()`/`stop()`,
or used as a context manager, which also stops it if the body raises:

```python
from beaupy.spinners import Spinner, DOTS

with Spinner(DOTS, text="Packing things..."):
    do_some_work()
```

To render on the same console as the other elements (e.g. a console you pass through `Config`), pass `console=`:

```python
Spinner(DOTS, text="Packing things...", console=my_console)
```

### Styling

#### Spinner Animation

There are few built in spinner animations, namely: ARC, ARROWS, BARS, CLOCK, DIAMOND, DOT, DOTS, LINE, LOADING and MOON

Each of these can be used in a spinner:

```python
from beaupy.spinners import Spinner, ARC
spinner = Spinner(ARC, text="Doing some heavy work")
spinner.start()
```

All that "animations" are, is but a list of string, so making your own is as trivial as this:

```python
from beaupy.spinners import Spinner
spinner = Spinner(['whee', 'whe ', 'wh  ', 'w   ', 'wh  ', 'whe ', 'whee'], text="Whee!")
spinner.start()
```

#### Rich styling

Every text in spinner does accept and respect rich styles, so the following works:

```python
from beaupy.spinners import Spinner
spinner = Spinner(['[red]⬤[/red] ', '[green]⬤[/green] ', '[blue]⬤[/blue] '], text='[pink1]Setting[/pink1] colors!')
spinner.start()
```

#### Animation speed

Animation speed can be set using `refresh_per_second` parameter:

```python
from beaupy.spinners import Spinner, LOADING
spinner = Spinner(LOADING, text="something", refresh_per_second=4)
spinner.start()
```

## Configuration

Each element accepts a `config` argument taking a `Config` instance. Options:

- `raise_on_interrupt`: If `True`, functions will raise `KeyboardInterrupt` whenever Ctrl+C is pressed when waiting for input,
        otherwise, they will return some sane alternative to their usual return. For `select`, `prompt` and `confirm` this means `None`,
        while for `select_multiple` it means an empty list - `[]`. Defaults to `True`.
- `raise_on_escape`: If `True`, functions will raise `Abort` whenever the escape key is encountered when waiting for input, otherwise,
        they will return some sane alternative to their usual return. For `select`, `prompt` and `confirm` this means `None`, while for
        `select_multiple` it means an empty list - `[]`.  Defaults to `False`.
- `transient`: If `False`, elements will remain displayed after their context has ended. Defaults to `True`.
- `console`: `rich.console.Console` the elements render to. Defaults to `Console(stderr=True, highlight=False)`.
- `keys`: `KeyBindings` used by the elements. Defaults to `KeyBindings()`.

```python
from beaupy import Config, select

# Ctrl+C raises KeyboardInterrupt by default; opt out to get `None` back instead
result = select(['Option 1', 'Option 2'], config=Config(raise_on_interrupt=False))
if result is None:
    print("User pressed Ctrl+C")
```

### Using your own console

Pass the console you already use, e.g. the one of a running `rich.live.Live`, so the two don't fight over the terminal:

```python
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from beaupy import Config, select_multiple

console = Console()
with Live(Panel("Foo"), console=console):
    select_multiple(list(range(15)), config=Config(console=console))
```

### Keybindings

```python
from beaupy import Config, KeyBindings, select

vim = Config(keys=KeyBindings(up=['k'], down=['j']))
select(['one', 'two'], config=vim)
```

## Title, instructions and sections

`select` and `select_multiple` take a `title` shown above the options. All elements take `instructions` shown below; pass `None` to hide it.

```python
select(['red', 'green'], title='Pick a color', instructions='([bold]enter[/bold] to pick)')
```

Pass a dict to show options in sections. Indices (`cursor_index`, `ticked_indices`, `return_index`, `return_indices`)
are then always `(section_name, index_within_section)` tuples; a plain `int` raises `TypeError` (and is flagged by type checkers):

```python
select_multiple({'Fruit': ['apple', 'pear'], 'Veg': ['leek']},
                ticked_indices=[('Veg', 0)],
                return_indices=True)  # e.g. [('Veg', 0), ('Fruit', 1)]
```

## Filtering

With `filterable=True`, typing narrows the options to those whose displayed text contains what was typed (case-insensitive,
markup ignored). Backspace removes the last typed character; the query is shown next to the title, along with a
`(matches/total)` count.

```python
select(['apple', 'banana', 'cherry'], title='Fruit', filterable=True)
```

Keys bound in `KeyBindings` keep their action, so in `select_multiple` space still ticks and `ctrl+a` ticks/unticks all visible options.

Ticked options stay ticked while hidden by the filter.

## Input validation

Empty `options` raises `ValueError` by default; pass `strict=False` to get `None` (`select`) or `[]` (`select_multiple`)
back instead:

```python
select(options=[])                 # raises ValueError
select(options=[], strict=False)   # returns None
```

`options` itself must be a sequence (or a dict of sections), never a bare string: `select('abc')` raises `TypeError` instead of
silently offering the letters.

A blank option (after preprocessing and stripping markup, e.g. `''`, `'   '`, or `'[red][/red]'`) or a blank section name
always raises `ValueError`, regardless of `strict` — there's no legitimate reason to want a menu row with nothing in it.

`confirm` applies the same rule to `yes_text`/`no_text`, and also raises if both labels start with the same letter while the
`(Y/N)` hint is shown (pass `char_prompt=False` or use different labels).

All elements read keypresses from the terminal, so they need an interactive one. When stdin isn't a TTY (piped input, most CI
runners), they raise `RuntimeError('Interactive terminal required')`.

## Migrating from 3.x

4.0.0 removes process-wide state and makes every argument after the first keyword-only.

| 3.x | 4.x |
|---|---|
| `Config.raise_on_escape = True` | `select(..., config=Config(raise_on_escape=True))` |
| `beaupy._beaupy.console = my_console` | `select(..., config=Config(console=my_console))` |
| `DefaultKeys.up.append('k')` | `select(..., config=Config(keys=KeyBindings(up=[Keys.UP_ARROW, 'k'])))` |
| `select(options, my_preprocessor)` | `select(options, preprocessor=my_preprocessor)` |
| `a` ticks/unticks all in `select_multiple` | `ctrl+a`; restore with `KeyBindings(select_all=['a'])` |
| `Spinner(DOTS, "text")` | `Spinner(DOTS, text="text")` (options are keyword-only); also usable as `with Spinner(...):` |
| Ctrl+C returns `None`/`[]` (`raise_on_interrupt=False`) | Raises `KeyboardInterrupt`; pass `Config(raise_on_interrupt=False)` for the old behavior |
| `strict` defaults to `False` (empty `options` returns `None`/`[]`) | Defaults to `True` (raises `ValueError`); pass `strict=False` for the old behavior |

`ValidationError` and `ConversionError` (from `prompt`) are now `ValueError` subclasses, so `except ValueError` catches them too.

`Keys` above comes from `yakh.key`. Using a removed global raises `RemovedInV4Error` (or `AttributeError` when assigning on `Config`/`KeyBindings`) with a message explaining the replacement.
