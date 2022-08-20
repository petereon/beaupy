#! /usr/bin/env python3
"""Example script demonstrating usage of cutie.
"""

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


if __name__ == "__main__":
    main()
