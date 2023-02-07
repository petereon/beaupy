#! /usr/bin/env python3
"""Example script demonstrating usage of beaupy.
"""

import time
from beaupy import *
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
