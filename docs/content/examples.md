# More Examples

## `select`/`select_multiple`

### Functionality

#### Return index

Selective elements default to return the selected item (in case of `select`) or list of items (in case of `select_multiple`). This behavior can be modified by `return_index` parameter (or `return_indices` in case of the latter), see example,

```python
result_index = select(option=['select', 'one'], 
                      return_index=True)
```

#### Starting cursor index

By default cursor is placed on the first element, this can be configured by `cursor_index` parameter as follows,

```python
results = select_multiple(['options', 'to', 'select', 'from'],
                           cursor_index=2)
```

### Styling

!!! tip
    For styling you can leverage [numerous styling options](https://rich.readthedocs.io/en/stable/style.html) provided by rich

#### Style as text

```python
result = select(options = ["red", "on", "white"], 
                cursor = "x", 
                cursor_style= "red on white")
```

#### Style as hex

```python
result_list = select_multiple(options = ["ok", "ko"], 
                              tick_character = "k", 
                              tick_style="#af00ff)
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
result = select_multiple(options = ["this", "other thing"], 
                tick_character = "selected")
```