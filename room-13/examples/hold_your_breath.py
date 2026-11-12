"""A minigame you could build yourself, in one function.

A minigame is just a function that an option runs. It does what it wants, and
then returns the name of the scene to go to. No special classes needed.

Here the player hides. Press a key too early and it hears you. Press too late
and it catches you. wait_for_key() does the timing.

Run it with:  poetry run python examples/hold_your_breath.py
"""
from textquest.effects import say, wait_for_key
from textquest.game import Game
from textquest.scene import Option, Scene


def hold_your_breath(game):
    say("Footsteps. Right outside the door.")
    say("[whisper]Don't press anything...[/]")

    if wait_for_key(game.random.uniform(2, 5)):
        say("[blood]It heard you.[/]")
        return "caught"

    say("[blood]NOW! PRESS A KEY AND RUN![/]", speed=0)

    if wait_for_key(1):
        return "escaped"
    say("[blood]Too slow.[/]")
    return "caught"


def make_game():
    game = Game("Hold Your Breath", start="closet")
    game.add(
        Scene("closet", title="The Closet",
              text="You're hiding in a closet. Something is coming down the hall.",
              options=[Option("Hide and wait", action=hold_your_breath)]),
        Scene("escaped", title="Gone", text="You run. You don't look back.", ending="win"),
        Scene("caught", title="Found", text="The closet door opens.", ending="lose"),
    )
    return game


if __name__ == "__main__":
    make_game().run()
