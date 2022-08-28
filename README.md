# BeauPy

![beaupy](https://user-images.githubusercontent.com/47027005/185082011-cb588f57-d38f-42d8-8312-3981ae1bc479.png)

> A Python library of interactive CLI elements you have been looking for

---

[![Tests](https://github.com/petereon/beaupy/actions/workflows/python-test.yml/badge.svg)](https://github.com/petereon/beaupy/actions/workflows/python-test.yml)
[![Lint](https://github.com/petereon/beaupy/actions/workflows/python-lint.yml/badge.svg)](https://github.com/petereon/beaupy/actions/workflows/python-lint.yml)
[![codecov](https://codecov.io/gh/petereon/beaupy/branch/master/graph/badge.svg?token=HSG6MGTXBC)](https://codecov.io/gh/petereon/beaupy)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=petereon_beaupy&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=petereon_beaupy)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=petereon_beaupy&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=petereon_beaupy)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=petereon_beaupy&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=petereon_beaupy)

For documentation but more and prettier see [**here**](https://petereon.github.io/beaupy/)

## Acknowledgment

BeauPy stands on the shoulders of giants. It is based on another library with which it shares some of the source code, [`cutie`](https://github.com/kamik423/cutie), developed by [Kamik423](https://github.com/Kamik423). It has begun as a fork but has since diverged into it's own thing and as such, detached from the original repository.

## Overview

**BeauPy** implements a number of common interactive elements:

| Function                                                                                                  | Functionality                                                                              |
|:----------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------|
| [`select`](https://petereon.github.io/beaupy/api/#select)                        | Prompt to pick a choice from a list                                                        |
| [`select_multiple`](https://petereon.github.io/beaupy/api/#select_multiple)      | Prompt to select one or multiple choices from a list                                       |
| [`confirm`](https://petereon.github.io/beaupy/api/#confirm)                      | Prompt with a question and yes/no options                                                  |
| [`prompt`](https://petereon.github.io/beaupy/api/#prompt)                        | Prompt that takes free input with optional validation, type conversion and input hiding |

## Getting Started

**BeauPy** is a library of interactive TUI elements for CLI applications.

**BeauPy** is

- [rich](https://rich.readthedocs.io/en/stable/) friendly
- stylable
- opinionated
- configurable

### Installation

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

### Example

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

        name = beaupy.select(names, cursor_index=3, cursor="🏰")
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
        nemeses = beaupy.select_multiple(nemeses_options)
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

For more information refer to [more_examples](https://petereon.github.io/beaupy/examples/) or definitive, but much less exciting [api documentation](https://petereon.github.io/beaupy/api/)

## Roadmap

This repository has a [associated GitHub project](https://github.com/users/petereon/projects/3/views/1) where work that is currently done can be seen

## Contributing

If you want to contribute, please feel free to suggest features or implement them yourself.

Also **please report any issues and bugs you might find!**

### Development

To start development you can clone the repository:

```sh
git clone https://github.com/petereon/beaupy.git
```

Change the directory to the project directory:

```sh
cd ./beaupy/
```

This project uses [`poetry`](https://python-poetry.org/) as a dependency manager. You can install the dependencies using:

```sh
poetry install
```

For testing, this project relies on [`ward`](https://github.com/darrenburns/ward). It is included as a development dependency, so
after installing the dependencies you can simply execute the following:

```sh
poetry run poe test
```

After you have made your changes, create a pull request towards a master branch of this repository

Looking forward to your pull requests!

## License

The project is licensed under the [MIT License](LICENSE).
