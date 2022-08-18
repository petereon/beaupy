![beaupy](https://user-images.githubusercontent.com/47027005/185082011-cb588f57-d38f-42d8-8312-3981ae1bc479.png)


> A Python library of interactive CLI elements you have been looking for

---

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=petereon_beaupy&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=petereon_beaupy) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=petereon_beaupy&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=petereon_beaupy) [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=petereon_beaupy&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=petereon_beaupy)

## Acknowledgment
BeauPy stands on the shoulders of giants. It is based on another library with which it shares some of the source code, [`cutie`](https://github.com/kamik423/cutie), developed by [Kamik423](https://github.com/Kamik423). It has begun as a fork but has since diverged into it's own thing and as such, detached from the original repository.

# Overview

**BeauPy** implements a number of common interactive elements:

| Function                                                                                                  | Functionality                                                                              |
|:----------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------|
| [`select`](https://github.com/petereon/beaupy/blob/master/APIDOC.md#beaupy.select)                        | Prompt to pick a choice from a list                                                        |
| [`select_multiple`](https://github.com/petereon/beaupy/blob/master/APIDOC.md#beaupy.select_multiple)      | Prompt to select one or multiple choices from a list                                       |
| [`confirm`](https://github.com/petereon/beaupy/blob/master/APIDOC.md#beaupy.confirm)                      | Prompt with a question and yes/no options                                                  |
| [`prompt`](https://github.com/petereon/beaupy/blob/master/APIDOC.md#beaupy.prompt)                        | Prompt that takes free input with optional validation, type conversion and input hiding |

## Usage

![example](https://raw.githubusercontent.com/petereon/beaupy/master/example.gif)

TUI elements shown in the above gif are the result of the follwing code:

```python
import beaupy


def main():
    """Main."""
    if beaupy.confirm("Are you brave enough to continue?"):
        names = [
            "Arthur, King of the Britons",
            "Sir Lancelot the Brave",
            "Sir Robin the Not-Quite-So-Brave-as-Sir-Lancelot",
            "Sir Bedevere the Wise",
            "Sir Galahad the Pure",
        ]

        name = names[beaupy.select(names, cursor_index=3)]
        print(f"Welcome, {name}")
        # Get an integer greater or equal to 0
        age = beaupy.prompt("What is your age?", target_type=int, validator=lambda val: val > 0)
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
        nemeses_indices = beaupy.select_multiple(nemeses_options)
        nemeses = [
            nemesis
            for nemesis_index, nemesis in enumerate(nemeses_options)
            if nemesis_index in nemeses_indices
        ]
        # Get input without showing it being typed
        quest = beaupy.prompt("What is your quest?", secure=True)
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

From PyPI:

```sh
pip install beaupy
```

From source:

```sh
git clone https://github.com/petereon/beaupy.git
poetry build
pip install ./dist/beaupy-{{some-version}}-py3-none-any.whl
```

## Documentation

**BeauPy** is a library of interactive TUI elements for CLI applications.

**BeauPy** is

- [rich](https://rich.readthedocs.io/en/stable/) friendly
- stylable
- opinionated
- configurable

<!-- TODO: extend docs a bit  -->

For API doc, please refer to [`APIDOC.md`](https://github.com/petereon/beaupy/blob/master/APIDOC.md)

## Roadmap

This repository has a [associated GitHub project](https://github.com/users/petereon/projects/3/views/1) where work that is currently done can be seen

## Contributing

If you want to contribute, please feel free to suggest features or implement them yourself.

Also **please report any issues and bugs you might find!**

## License

The project is licensed under the [MIT License](LICENSE).
