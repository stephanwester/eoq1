"""Play a short video in your game. It opens in its own window, and any key skips it.

Use Scene(video=...) to play it when the player arrives, or play_video() in your
own function. Film your own clips: even a shaky phone video of a dark hallway works.

Run it with:  poetry run python examples/video.py
"""
from pathlib import Path

from textquest.game import Game
from textquest.scene import Option, Scene

CLIP = Path(__file__).parent / "media" / "the_door.mp4"


def make_game():
    game = Game("The Tape", start="tv")
    game.add(
        Scene("tv", title="The Old TV",
              text="A dusty TV on a cart. There's a tape in it, with [bold]13[/] on the label.",
              options=[Option("Press play", "tape")]),
        Scene("tape", title="Static", video=CLIP,
              text="The tape stops.[pause] [whisper]The door on the tape looks a lot like the one behind you.[/]",
              ending="lose"),
    )
    return game


if __name__ == "__main__":
    make_game().run()
