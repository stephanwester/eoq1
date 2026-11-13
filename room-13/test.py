"""Testing: 1 scenes and a way out.

Run it with:  poetry run python test.py
"""

from textquest.game import Game
from textquest.scene import Option, Scene
from textquest.effects import say, static, flicker
from crying_girl import interact_with_girl, open_door
from secret_room import enter_secret_room, riddle1, riddle2, riddle3
from examples.rad import make_game as make_game1
from examples.snake_game.main import play_snake_game as make_game2
from examples.shoot_the_pies import make_game as make_game3

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

ARCADE_ACII = """
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


# functions
def read_poster(game):
    say("""
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
   
""", speed=0.05)


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
            say("Congrats on beating the game!")
            game.set("beat_game1")
            game.change("mini game wins", +1)
        else:
            say("You didn't beat the game... Good luck with the other ones")
            game.set("lost_game1")
    else:
        say("The machine looks powered off")


def load_game2(game):
    if game.get("powered_game2") and not game.get("beat_game2"):
        flicker()
        static(0.5)
        result = make_game2()
        game.set("powered_game2", False)
        if result:
            say("Congrats on beating the game!")
            game.set("beat_game2")
            game.change("mini game wins", +1)
        else:
            say("You didn't beat the game... Good luck with the other ones")
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
            say("Congrats on beating the game!")
            game.set("beat_game3")
            game.change("mini game wins", +1)
        else:
            say("You didn't beat the game... Good luck with the other ones")
            game.set("lost_game3")
    else:
        say("The machine looks powered off")


def choose_ending(game):
    say("You chose to leave the arcade hall... \nYour fate will be decided...")
    if game.get("mini game wins") == 1:
        return "bad"
    if game.get("mini game wins") >= 2:
        return "good"
    return "nothing"


#  play game functionality
def main_game():
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
                Option("Walk out of the arcade", "outside"),
                Option("Look at the poster", action=read_poster),
                Option("Look at machine 1", "machine 1"),
                Option("Look at machine 2", "machine 2"),
                Option("Look at machine 3", "machine 3"),
                Option("Approach the crying girl", action=interact_with_girl),
                Option("Open the mysterious door", action=open_door),
            ],
        )
    )

    game.add(
        Scene(
            "machine 1",
            title="Machine 1",
            text=LUCK_INTRO,
            options=[
                Option(
                    "Insert a coin",
                    action=lambda game: insert_coin(game, 1),
                    condition=lambda game: not bool(game.get("powered_game1"))
                    and not bool(game.get("beat_game1")),
                ),
                Option(
                    "Play the game",
                    action=load_game1,
                    condition=lambda game: bool(game.get("powered_game1"))
                    and not bool(game.get("beat_game1")),
                ),
                Option("Go Back", "arcade"),
            ],
        )
    )

    game.add(
        Scene(
            "machine 2",
            title="Machine 2",
            text=SNAKE_INTRO,
            options=[
                Option(
                    "Insert a coin",
                    action=lambda game: insert_coin(game, 2),
                    condition=lambda game: not bool(game.get("powered_game2"))
                    and not bool(game.get("beat_game2")),
                ),
                Option(
                    "Play the game",
                    action=load_game2,
                    condition=lambda game: bool(game.get("powered_game2"))
                    and not bool(game.get("beat_game2")),
                ),
                Option("Go Back", "arcade"),
            ],
        )
    )

    game.add(
        Scene(
            "machine 3",
            title="Machine 3",
            text=SHOOTING_INTRO,
            options=[
                Option(
                    "Insert a coin",
                    action=lambda game: insert_coin(game, 3),
                    condition=lambda game: not bool(game.get("powered_game3"))
                    and not bool(game.get("beat_game3")),
                ),
                Option(
                    "Play the game",
                    action=load_game3,
                    condition=lambda game: bool(game.get("powered_game3"))
                    and not bool(game.get("beat_game3")),
                ),
                Option("Go Back", "arcade"),
            ],
        )
    )
    game.add(
        Scene(
            "secret room",
            title="Secret Room",
            text="You step into a dark room. The air feels strangely cold.",
            options=[
                Option("Explore the secret room", action=enter_secret_room),
                Option("Return to the arcade", "arcade"),
                Option("Look at the table", action=table, condition=lambda game: bool(game.get("secret_explored"))),
                Option("Look at riddle 1", action=riddle1, condition=lambda game: bool(game.get("secret_explored"))),
                Option("Look at riddle 2", action=riddle2, condition=lambda game: bool(game.get("secret_explored"))),
                Option("Look at riddle 3", action=riddle3, condition=lambda game: bool(game.get("secret_explored"))),
            ],
        )
    )

    game.add(
        Scene(
            "outside",
            title="Outside",
            text="Cold air. You made it outside.[pause] You hear a whispering voice behind you too unclear to make out.",
            options=[Option("Continue", action=choose_ending),
                     Option("Go back inside", "arcade")],
        )
    )

    # TODO endings
    game.add(
        Scene(
            "good",
            title="Good Gamer",
            ending="win",
            text=lambda game: f"{game.get('keys')} mini games beaten!",
        ),
        Scene(
            "bad",
            title="Bad Gamer",
            ending="lose",
            text=lambda game: f"Only {game.get('keys')} earned...",
        ),
        Scene("nothing", title="Did Nothing", ending="lose", text="No games beaten..."),
    )
    return game


if __name__ == "__main__":
    main_game().run()
