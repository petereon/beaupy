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
        # Get the index of selected option
        name = names[pytui.select(names, selected_index=4)]
        print(f"Welcome, {name}")
        # Get an integer greater or equal to 0
        age = pytui.prompt_number("What is your age?", min_value=0, allow_float=False)
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
        quest = pytui.prompt_secure("What is your quest?")
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

From source:
```sh
git clone https://github.com/petereon/pytui.git
poetry build
pip install ./dist/pytui-{{some-version}}-py3-none-any.whl
```

## Documentation
!include docs/apidoc.md

## Contributing

If you want to contribute, please feel free to suggest features or implement them yourself.

Also **please report any issues and bugs you might find!**

## License

The project is licensed under the [MIT-License](LICENSE).
