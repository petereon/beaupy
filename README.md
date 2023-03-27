# BeauPy

![beaupy](https://user-images.githubusercontent.com/47027005/185082011-cb588f57-d38f-42d8-8312-3981ae1bc479.png)

> A Python library of interactive CLI elements you have been looking for

---

[![Tests](https://github.com/petereon/beaupy/actions/workflows/python-test.yml/badge.svg)](https://github.com/petereon/beaupy/actions/workflows/python-test.yml)
[![Lint](https://github.com/petereon/beaupy/actions/workflows/python-lint.yml/badge.svg)](https://github.com/petereon/beaupy/actions/workflows/python-lint.yml)
[![codecov](https://codecov.io/gh/petereon/beaupy/branch/master/graph/badge.svg?token=HSG6MGTXBC)](https://codecov.io/gh/petereon/beaupy)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=petereon_beaupy&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=petereon_beaupy)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=petereon_beaupy&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=petereon_beaupy)
![PyPI - Downloads](https://img.shields.io/pypi/dm/beaupy?color=g&label=%F0%9F%93%A5%20Downloads)

For documentation but more and prettier see [**here**](https://petereon.github.io/beaupy/)

## Acknowledgment

BeauPy stands on the shoulders of giants. It is based on another library with which it shares some of the source code, [`cutie`](https://github.com/kamik423/cutie), developed by [Kamik423](https://github.com/Kamik423). It has begun as a fork but has since diverged into it's own thing and as such, detached from the original repository.

## Overview

![example](https://raw.githubusercontent.com/petereon/beaupy/master/example.gif)

**BeauPy** implements a number of common interactive elements:

| Function                                                                                                  | Functionality                                                                              |
|:----------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------|
| [`select`](https://petereon.github.io/beaupy/api/#select)                        | Prompt to pick a choice from a list                                                        |
| [`select_multiple`](https://petereon.github.io/beaupy/api/#select_multiple)      | Prompt to select one or multiple choices from a list                                       |
| [`confirm`](https://petereon.github.io/beaupy/api/#confirm)                      | Prompt with a question and yes/no options                                                  |
| [`prompt`](https://petereon.github.io/beaupy/api/#prompt)                        | Prompt that takes free input with optional validation, type conversion and input hiding |

TUI elements shown in the above gif are the result of the follwing code:

```python
import time
from beaupy import confirm, prompt, select, select_multiple
from beaupy.spinners import *


# Confirm a dialog
if confirm("Will you take the ring to Mordor?"):
    names = [
        "Frodo Baggins",
        "Samwise Gamgee",
        "Legolas",
        "Aragorn",
        "[red]Sauron[/red]",
    ]
    console.print("Who are you?")
    # Choose one item from a list
    name = select(names, cursor="🢧", cursor_style="cyan")
    console.print(f"Alámenë, {name}")
    
    
    item_options = [
        "The One Ring",
        "Dagger",
        "Po-tae-toes",
        "Lightsaber (Wrong franchise! Nevermind, roll with it!)",
    ]
    console.print("What do you bring with you?")
    # Choose multiple options from a list
    items = select_multiple(item_options, tick_character='🎒', ticked_indices=[0], maximal_count=3)
    
    potato_count = 0
    if "Po-tae-toes" in items:
        # Prompt with type conversion and validation
        potato_count = prompt('How many potatoes?', target_type=int, validator=lambda count: count > 0)
    
    # Spinner to show while doing some work
    spinner = Spinner(DOTS, "Packing things...")
    spinner.start()
    
    time.sleep(2)
    
    spinner.stop()
    # Get input without showing it being typed
    if "friend" == prompt("Speak, [blue bold underline]friend[/blue bold underline], and enter", secure=True).lower():
        
        # Custom spinner animation
        spinner_animation = ['▉▉', '▌▐', '  ', '▌▐', '▉▉']
        spinner = Spinner(spinner_animation, "Opening the Door of Durin...")
        spinner.start()
        
        time.sleep(2)
        
        spinner.stop()
    else:
        spinner_animation = ['🐙🌊    ⚔️ ', '🐙 🌊   ⚔️ ', '🐙  🌊  ⚔️ ', '🐙   🌊 ⚔️ ', '🐙    🌊⚔️ ']
        spinner = Spinner(spinner_animation, "Getting attacked by an octopus...")
        spinner.start()
        
        time.sleep(2)
        
        spinner.stop()

    if 'The One Ring' in items:
        console.print("[green]You throw The One Ring to a lava from an eagle![/green]")
    else:
        console.print("[red]You forgot the ring and brought Middle-Earth to its knees![/red]")
    console.print(f"And you brought {potato_count} taters!")      
```

For more information refer to [more examples](https://petereon.github.io/beaupy/examples/) or definitive, but much less exciting [API documentation](https://petereon.github.io/beaupy/api/)

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

## Roadmap

This repository has a [associated GitHub project](https://github.com/users/petereon/projects/3/views/1) where work that is currently done can be seen.

## Contributing

If you would like to contribute, please feel free to suggest features or implement them yourself.

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

Making sure the code follows quality standards and formatting can be ensured by executing

```sh
poetry run poe lint
```

You can also have the tests and lints run after every saved change by executing a respective watch command

```sh
poetry run poe test:watch
```

or

```sh
poetry run poe lint:watch
```

After you have made your changes, create a pull request towards a master branch of this repository

Looking forward to your pull requests!

## Compatibility

Internal logic of `beaupy` is supported for all the major platforms (Windows, Linux, macOS).

- For user input from console, `beaupy` relies on [petereon/yakh](https://github.com/petereon/yakh), which is tested against all the major platforms and Python versions.
- For printing to console `beaupy` relies on [Textualize/rich](https://github.com/Textualize/rich), which [claims to support](https://github.com/Textualize/rich#compatibility) all the major platforms.

## Known Issues

- Version `2.x.x` reportedly does not always support arrow keys on Windows. 

## Awesome projects using `beaupy`

- [therealOri/Genter](https://github.com/therealOri/Genter): A strong password generator and built in password manager made with python3!
- [therealOri/byte](https://github.com/therealOri/byte): Steganography Image/Data Injector. For artists or people to inject their own Datamark "Watermark" into their images/art or files!

## License

The project is licensed under the [MIT License](LICENSE).
