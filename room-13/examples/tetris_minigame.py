"""An adventure with a game of Tetris in it.

An option runs seal_the_cabinet(), which starts Tetris and uses the result to pick
the next scene. Tetris has no rules for this game: the two small functions below add them.

Run it with:  poetry run python examples/tetris_minigame.py
"""
from tetris.game import Tetris
from tetris.pieces import CLASSIC, Piece
from textquest.game import Game
from textquest.scene import Option, Scene

SECONDS = 60

SKULL = Piece("skull", """
    .#.
    ###
    .#.
""", "white", weight=0.3)


def close_a_lock(tetris):
    """Runs when lines are cleared: every line closes a lock."""
    tetris.info["Locks left"] -= tetris.just_cleared
    tetris.shake()
    if tetris.info["Locks left"] <= 0:
        tetris.end(won=True)


def countdown(tetris):
    """Runs every second: when the time is up, you lose."""
    tetris.info["Time left"] = SECONDS - int(tetris.time)
    if tetris.info["Time left"] <= 0:
        tetris.end(won=False)


def make_tetris():
    return Tetris(
        title="SEAL THE CABINET",
        message="Every line you clear closes a lock. Hurry!",
        pieces=[*CLASSIC, SKULL],
        info={"Locks left": 5, "Time left": SECONDS},
        on_clear=close_a_lock,
        on_second=countdown,
    )


def seal_the_cabinet(game):
    """Runs in the adventure when the player picks the option."""
    result = make_tetris().play()
    game.change("courage", result["score"] // 100)
    if result["won"]:
        return "sealed"
    return "too_late"


def make_game():
    game = Game("The Cabinet", start="room", stats={"courage": 0})
    game.add(
        Scene("room", title="Room 13",
              text="The cabinet is shaking. [blood]Something[/] wants to get out. "
                   "The screen shows falling blocks.",
              options=[Option("Grab the controls", action=seal_the_cabinet)]),
        Scene("sealed", title="Silence", text="The last lock clicks. The screen goes dark.", ending="win"),
        Scene("too_late", title="Too Late", text="The screen cracks. A hand comes out.", ending="lose"),
    )
    return game


if __name__ == "__main__":
    make_game().run()
