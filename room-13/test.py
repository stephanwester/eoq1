"""Testing: 1 scenes and a way out.

Run it with:  poetry run python test.py
"""

from secret_room import enter_secret_room, riddle1, riddle2, riddle3, table, safe_cracking, collect_coins, DOCUMENTS
from examples.snake_game.main import play_snake_game as make_game2
from examples.shoot_the_pies import make_game as make_game3
from examples.rad import make_game as make_game1
from crying_girl import interact_with_girl, open_door
from textquest.effects import say, static, flicker
from textquest.scene import Option, Scene
from textquest.game import Game
from textquest.sound import play_sound
from pathlib import Path

MUSIC = Path(__file__).parent / "examples" / "media" / "background.mp3"

TIME_SECONDS = 30
KEYS_NEEDED = 2

SNAKE_INTRO = """
Welcome to the Cursed Snake Game...

13 souls are trapped inside this arcade machine.
Collect them all to break the curse and set them free.

But beware... you have only three lives.
Fail, and your soul will join them for eternity.

Will you break the curse, or become part of it?
"""

LUCK_INTRO = """
Welcome to the Wheel of Misfortune!

One spin. Only one way to win.

Feeling lucky?

Don't worry, Kitty is rooting for you...

Or is she?
"""

SHOOTING_INTRO = """
Welcome to Apple Waster!

So many apples, so little time...

Fire away and hit those pies!
Who cares about wasting a few apples?

It's not like there are people starving somewhere...

Anyway, ready to play?
"""

FIRST_TEXT = """
You open your eyes.

Where... are you?

You can't remember how you got here. In fact, you can't remember anything... except your name.

You're standing in an abandoned arcade. Three old machines flicker, seemingly wanting to come alive.

Behind you is an exit door with a strange poster beside it.

Somewhere in the corner, you hear a little girl crying.

Something about this place feels strangely familiar...

You feel in your pockets and find 3 coins.
"""

NORMAL_ARCADE = """
You a door on one wall with an exit sign above it and a poster next to it.
On another wall you see 3 arcade machines lined up.
In a corner there is the little girl with an old looking door next to it.
"""

NORMAL_ARCADE_ASCII = """
 ____________________________________________________________
|                                                            |
|    .------.        .------.        .------.                |
|    |######|        |######|        |######|                |
|    |#Luck#|        |#Free#|        |#Fill#|                |
|    |######|        |######|        |######|                |
|    '------'        '------'        '------'                |
|    | o  + |        | o  + |        | o  + |                |
|    | /--\\ |        | /--\\ |        | /--\\ |                |
|    |_|__|_|        |_|__|_|        |_|__|_|                |
|    |   1  |        |   2  |        |   3  |                |
|    |______|        |______|        |______|                |
|                                                            |
|                                                            |
|  ____                                                      |
| |    |   o                                ___       ____   |
| |DOOR|  /|\\                              |   |     |    |  |
| |  ? |  / \\                              |   |     |EXIT|  |
| |   o|  little                           |___|     | 1 o|  |
| |    |  girl                                       |    |  |
|_|____|_____________________________________________|____|__|
"""

ARCADE_ASCII = """
⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⠀
⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠀
⠀⢠⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⡄⠀⠀
⠀⢸⣿⣿⡟⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⢻⣿⣿⡇⠀⠀
⠀⢸⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⡇⠀⠀
⠀⢸⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⡇⠀⠀
⠀⢸⣿⣿⣧⣀⣀⠀⣴⣿⣿⣦⠀⣀⣀⣼⣿⣿⡇⠀⠀
⠀⠸⠿⠿⠿⠿⠿⠄⠘⣿⣿⠃⠠⠿⠿⠿⠿⠿⠇⠀⠀
⠀⣤⣤⣤⣤⣤⣤⣤⠀⣿⣿⠀⣤⣤⣤⣤⣤⣤⣤⠀⠀
⢰⣿⣿⣿⣿⣿⣿⣿⣄⡈⢁⣠⣿⣿⣿⣿⣿⣿⣿⣧⠀
⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠂
⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⡆
⠻⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠃
"""

SAFE_ASCII = """
 ________________________________________
 │                                      │
 │                                      │
 │                   ┌─────┐            │
 │                   │ xxx │            │
 │   \\   /           │ xxx │   ______   │
 │    \\ /            │ xxx │   |    |   │
 │  ---0---          └─────┘   |    |   │
 │    / \\                      |    |   │
 │   /   \\                     |____|   │
 │                                      │
 │                                      │
 │                                      │
 │                                      │
 │______________________________________│
                                         
"""

SECRET_ROOM_ASCII = """
┌─────────────────────────────────┐
│         ┌───┐┌───┐┌───┐         │
│         └───┘└───┘└───┘         │
│                                 │
│┌─┐            ,-.               │
│└─┘           (   )              │
│               `-'        ╓───╖  │
│                          ║   ║  │
│                          ║   ║  │
└──────────────────────────╙───╜──┘
"""

SAFE_TEXT = """
You inspect the safe and see a num pad where you can enter a 3 digit code.
There is a sticky note next to it
"""

NOTE_TEXT = '\"If you forgot the code to the safe, just solve the riddles\"'


POSTER = """
    _________________________________
   |                                 |
   |      WELCOME TO THE ARCADE!     |
   |                                 |
   |         Three games.            |
   |  Win two to earn your freedom.  |
   |                                 |
   |      Fail to win enough...      |
   |  And stay and play forever.     |
   |                                 |
   |_________________________________|
"""


# functions
def read_poster(game):
    say(POSTER)


def read_documents(game):
    say(DOCUMENTS)


def read_note(game):
    say("The note reads:\n" + NOTE_TEXT)


def insert_coin(game, game_number):
    beat_flag = f"beat_game{game_number}"
    lost_flag = f"lost_game{game_number}"
    powered_flag = f"powered_game{game_number}"
    if game.get(beat_flag):
        say("This game has already been beaten. The machine stays powered off.")
    elif game.get(powered_flag):
        say("The machine is already powered on.")
    else:
        if game.get("coins", 0) < 1:
            say("You need a coin to power the machine on.")
            return
        game.change("coins", -1)
        game.set(lost_flag, False)
        game.set(powered_flag)
        say("You insert a coin. The machine powers on.")


def load_game1(game):
    if game.get("powered_game1") and not game.get("beat_game1"):
        flicker()
        static(0.5)
        result = make_game1()
        game.set("powered_game1", False)
        if result:
            say("How sweet you won...\nDon't let it get to your head.")
            game.set("beat_game1")
            game.change("mini game wins", +1)
        else:
            say("Guess Kitty wasn't rooting...\nBut then again, is anyone?")
            game.set("lost_game1")
    else:
        say("The machine looks powered off")
    play_sound(MUSIC, -1)


def load_game2(game):
    if game.get("powered_game2") and not game.get("beat_game2"):
        flicker()
        static(0.5)
        result = make_game2()
        game.set("powered_game2", False)
        if result:
            say("Congrats the souls are freed!\nLet's hope they stay away.")
            game.set("beat_game2")
            game.change("mini game wins", +1)
        else:
            say("13 souls remain trapped.\nI'm sure you have other talents...")
            game.set("lost_game2")
    else:
        say("The machine looks powered off")


def load_game3(game):
    if game.get("powered_game3") and not game.get("beat_game3"):
        flicker()
        static(0.5)
        result = make_game3()
        game.set("powered_game3", False)
        if result:
            say("Wonderful, you hit all those pies!\nYou must be so proud of yourself...")
            game.set("beat_game3")
            game.change("mini game wins", +1)
        else:
            say("What a waste of apples...")
            game.set("lost_game3")
    else:
        say("The machine looks powered off")


def choose_ending(game):
    say("You chose to leave the arcade hall... \nYour fate will be decided...")
    if game.get("mini game wins") >= 2:
        return "good"
    if game.get("talked_to_lily") or game.get("lost_game1") or game.get("lost_game2") or game.get("lost_game3") or game.get("safe unlocked"):
        return "bad"
    return "nothing"


#  play game functionality
def main_game():
    play_sound(MUSIC, -1)
    game = Game(
        "Haunted Arcade",
        start="arcade",
        subtitle="Play the games or suffer the consequences",
        stats={"mini game wins": 0, "coins": 3},
    )

    game.add(
        Scene(
            "arcade",
            title="Arcade",
            first_text=FIRST_TEXT + NORMAL_ARCADE_ASCII,
            text=NORMAL_ARCADE_ASCII + NORMAL_ARCADE,
            options=[
                Option("Look at machine 1", "machine 1"),
                Option("Look at machine 2", "machine 2"),
                Option("Look at machine 3", "machine 3"),
                Option("Look at the poster", action=read_poster),
                Option("Approach the crying girl",
                       action=interact_with_girl,
                       condition=lambda game: bool(not game.get("girl_disappeared"))),
                Option("Open the mysterious door", action=open_door),
                Option("Walk out of the arcade", "outside"),
            ],
        )
    )

    game.add(
        Scene(
            "machine 1",
            title="Wheel of Misfortune",
            text=LUCK_INTRO + ARCADE_ASCII,
            options=[
                Option(
                    "Insert a coin",
                    action=lambda game: insert_coin(game, 1),
                    condition=lambda game: (
                        not bool(game.get("powered_game1"))
                        and not bool(game.get("beat_game1"))
                    ),
                ),
                Option(
                    "Play the game",
                    action=load_game1,
                    condition=lambda game: (
                        bool(game.get("powered_game1"))
                        and not bool(game.get("beat_game1"))
                    ),
                ),
                Option("Go Back", "arcade"),
            ],
        )
    )

    game.add(
        Scene(
            "machine 2",
            title="Cursed Snake",
            text=SNAKE_INTRO + ARCADE_ASCII,
            options=[
                Option(
                    "Insert a coin",
                    action=lambda game: insert_coin(game, 2),
                    condition=lambda game: (
                        not bool(game.get("powered_game2"))
                        and not bool(game.get("beat_game2"))
                    ),
                ),
                Option(
                    "Play the game",
                    action=load_game2,
                    condition=lambda game: (
                        bool(game.get("powered_game2"))
                        and not bool(game.get("beat_game2"))
                    ),
                ),
                Option("Go Back", "arcade"),
            ],
        )
    )

    game.add(
        Scene(
            "machine 3",
            title="Apple Waster",
            text=SHOOTING_INTRO + ARCADE_ASCII,
            options=[
                Option(
                    "Insert a coin",
                    action=lambda game: insert_coin(game, 3),
                    condition=lambda game: (
                        not bool(game.get("powered_game3"))
                        and not bool(game.get("beat_game3"))
                    ),
                ),
                Option(
                    "Play the game",
                    action=load_game3,
                    condition=lambda game: (
                        bool(game.get("powered_game3"))
                        and not bool(game.get("beat_game3"))
                    ),
                ),
                Option("Go Back", "arcade"),
            ],
        )
    )
    game.add(
        Scene(
            "secret room",
            title="Secret Room",
            first_text="You step into a dark room. The air feels strangely cold." + SECRET_ROOM_ASCII,
            text=SECRET_ROOM_ASCII,
            options=[
                Option("Look at riddle 1", action=riddle1, condition=lambda game: bool(game.get("secret_explored"))),
                Option("Look at riddle 2", action=riddle2, condition=lambda game: bool(game.get("secret_explored"))),
                Option("Look at riddle 3", action=riddle3, condition=lambda game: bool(game.get("secret_explored"))),
                Option("Look at the safe", "safe", condition=lambda game: bool(game.get("secret_explored"))),
                Option("Look at the table", action=table, condition=lambda game: bool(game.get("secret_explored")), once=True),
                Option("Explore the secret room", action=enter_secret_room, condition=lambda game: bool(not game.get("secret_explored"))),
                Option("Return to the arcade", "arcade"),
            ],
        )
    )
    game.add(
        Scene(
            "safe",
            title="The Safe",
            text=SAFE_ASCII,
            options=[
                Option("Try and input a code", action=safe_cracking, condition=lambda game: bool(not game.get("safe unlocked"))),
                Option("Open the safe", "inside safe", condition=lambda game: bool(game.get("safe unlocked"))),
                Option("Read the note", action=read_note),
                Option("Back away", "secret room")
            ]
        ),
        Scene(
            "inside safe",
            text="Inside you find some documents and a small stash of coins.",
            options=[
                Option("Read documents", action=read_documents),
                Option("Collect the coins", action=collect_coins, once=True),
                Option("Back away", "secret room")

            ]
        )
    )

    game.add(
        Scene(
            "outside",
            title="Outside",
            text="Cold air. You made it outside.[pause] You hear a whispering voice behind you too unclear to make out.",
            options=[
                Option("Continue", action=choose_ending),
                Option("Go back inside", "arcade"),
            ],
        )
    )

    game.add(
    Scene("good", title="Good Ending", ending="win", text=""),
    Scene("bad", title="Bad Ending", ending="lose", text=""),
    Scene("nothing", title="Did Nothing", ending="lose", text=""),
)
    return game


if __name__ == "__main__":
    main_game().run()
