#! /usr/bin/env python3
"""Example script demonstrating usage of cutie.
"""

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


if __name__ == "__main__":
    main()
