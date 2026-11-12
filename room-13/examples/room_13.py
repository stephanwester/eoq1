"""A short horror game that shows most of what textquest can do.

It has items, stats, flags, a riddle with ask(), functions that change the text,
scary effects, and on_turn to end the game when the player's courage runs out.

Run it with:  poetry run python examples/room_13.py
"""
from pathlib import Path

from textquest.effects import ask, flicker, jumpscare, say, static
from textquest.game import Game
from textquest.scene import Option, Scene
from textquest.sound import play_sound

MEDIA = Path(__file__).parent / "media"

DOOR_ART = r"""
     ____________
    |  ________  |
    | |        | |
    | |   13   | |
    | |        | |
    | |      o | |
    | |        | |
    |_|________|_|
"""

CABINET_ART = r"""
      ___________
     |  _______  |
     | |       | |
     | | HELLO | |
     | |_______| |
     |   o  [ ]  |
     |___________|
"""


# ---------- functions for things that options can't do on their own ----------

def lights_go_out(game):
    """Runs every time the player enters the basement."""
    if not game.was_visited("basement"):
        flicker()


def riddle(game):
    """The cabinet asks a riddle. A right answer opens the back door."""
    answer = ask("""[italic]"I HAVE KEYS BUT I CAN'T OPEN A SINGLE LOCK. WHAT AM I?"[/]""")
    if "keyboard" in answer.lower() or "piano" in answer.lower():
        say('The screen goes dark.[pause] Behind the cabinet, something clicks.')
        game.set("riddle_solved")
    else:
        static(0.6)
        say("[blood]WRONG.[/][pause=0.5] The screen shows your name. How does it know?")
        game.change("courage", -3)


def open_locker(game):
    """Nothing good comes out of an old locker."""
    jumpscare(sound=MEDIA / "sting.wav")
    say("[blood]Something[/] was in there.[pause] Now it's gone. Where did it go?")
    game.change("courage", -4)


def heartbeat(game):
    """Runs when the player arrives. Your heart is the loudest thing down here."""
    if game.get("courage") <= 5:
        play_sound(MEDIA / "heartbeat.wav")


def check_courage(game):
    """Runs after every option. No courage left: the game is over."""
    if game.get("courage") <= 0:
        return "caught"
    return None


def corridor_text(game):
    if game.has("flashlight"):
        return "Your flashlight shows a row of lockers, and a door with [bold]13[/] on it."
    return "It's pitch black. You hear something breathing."


# ---------- the scenes ----------

def make_game():
    game = Game(
        "Room 13",
        start="stairs",
        subtitle="Friday the 13th, 23:58",
        stats={"courage": 10},
        items={
            "flashlight": "The caretaker's flashlight. The battery is almost empty.",
            "floor plan": "There's no room 13 on it.",
        },
        on_turn=check_courage,
    )

    game.add(Scene(
        "stairs",
        title="The Basement Stairs",
        first_text="The school is empty. You shouldn't be here.[pause] "
                   "The door to the basement is [italic]already open[/]. As if someone expected you.",
        text="The stairs creak under your feet.",
        options=[
            Option("Pick up the flashlight", give="flashlight", once=True,
                   text="It's still warm. Someone was here a moment ago."),
            Option("Read the note on the wall", give="floor plan", once=True,
                   text="A floor plan of the basement. Rooms 1 to 12."),
            Option("Go down", "basement"),
        ],
    ))

    game.add(Scene(
        "basement",
        title="The Basement",
        on_enter=lights_go_out,
        first_text="The lights go out.[pause] [slow]All of them.[/][pause] "
                   "Far away, a screen starts to glow.",
        text="Broken chairs. Dust. The glow is still there.",
        options=[
            Option("Walk towards the glow", "corridor"),
            Option("Run back up the stairs", "stairs"),
        ],
    ))

    game.add(Scene(
        "corridor",
        title="The Corridor",
        on_enter=heartbeat,
        text=corridor_text,
        options=[
            Option("Open a locker", action=open_locker, once=True),
            Option("Go into room 13", "room", needs="flashlight", show_locked=True),
            Option("Go back", "basement"),
        ],
    ))

    game.add(Scene(
        "room",
        title="Room 13",
        art=DOOR_ART,
        art_color="white",
        text="No windows. Only an old arcade cabinet.[pause] "
             "The cable is cut, but the screen is on.",
        options=[
            Option("Look at the screen", "cabinet"),
            Option("Open the back door", "exit", needs_flag="riddle_solved", show_locked=True),
            Option("Leave", "corridor"),
        ],
    ))

    game.add(Scene(
        "cabinet",
        title="The Cabinet",
        art=CABINET_ART,
        art_color="red",
        text="[whisper]It knows you're here.[/]",
        options=[
            Option("Answer the riddle", "room", action=riddle, unless_flag="riddle_solved"),
            Option("Step back", "room"),
        ],
    ))

    game.add(Scene(
        "exit",
        title="The Back Door",
        text="Cold air. You're outside.[pause] The clock strikes [bold]midnight[/].[pause=2] "
             "[glitch]Your phone starts to ring. The screen says: ROOM 13.[/]",
        ending="win",
    ))

    game.add(Scene(
        "caught",
        title="Nobody Home",
        text="Your legs stop working.[pause] Behind you, something starts to hum.",
        ending="lose",
    ))

    return game


if __name__ == "__main__":
    make_game().run()
