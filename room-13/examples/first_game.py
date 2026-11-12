"""The smallest useful game: three scenes and a way out.

Run it with:  poetry run python examples/first_game.py
"""
from textquest.game import Game
from textquest.scene import Option, Scene


def make_game():
    game = Game("Stay After Class", start="classroom")

    game.add(Scene(
        "classroom",
        title="An Empty Classroom",
        text="You fell asleep in class. It's dark outside. Everyone is gone.",
        options=[
            Option("Walk into the hallway", "hallway"),
        ],
    ))

    game.add(Scene(
        "hallway",
        title="The Hallway",
        text="The lights go on and off. [whisper]Someone is humming.[/] The exit is at the far end.",
        options=[
            Option("Go back to the classroom", "classroom"),
            Option("Run to the exit", "outside"),
        ],
    ))

    game.add(Scene(
        "outside",
        title="Outside",
        text="Cold air. You made it out.[pause] Behind you, the door slowly closes on its own.",
        ending="win",
    ))

    return game


if __name__ == "__main__":
    make_game().run()
