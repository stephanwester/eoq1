"""Testing: 1 scenes and a way out.

Run it with:  poetry run python test.py
"""
from textquest.game import Game
from textquest.scene import Option, Scene
from textquest.effects import say, static, flicker
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


# functions
def read_poster(game):
    say("Welcome to the arcade.\nBeat at least 2 games otherwise we will haunt you!")


def load_game1(game):
    if not game.get("beat_game1") and not game.get("lost_game1"):
        flicker()
        static(0.5)
        result = make_game1()
        if result:
            say("Congrats on beating the game!")
            game.set("beat_game1")
            game.change("key", +1)
        else:
            say("You didn't beat the game... Good luck with the other ones")
            game.set("lost_game1")
    else:
        say("The machine looks powered off")


def load_game2(game):
    if not game.get("beat_game2") and not game.get("lost_game2"):
        flicker()
        static(0.5)
        result = make_game2()
        if result:
            say("Congrats on beating the game!")
            game.set("beat_game2")
            game.change("key", +1)
        else:
            say("You didn't beat the game... Good luck with the other ones")
            game.set("lost_game2")
    else:
        say("The machine looks powered off")


def load_game3(game):
    if not game.get("beat_game3") and not game.get("lost_game3"):
        flicker()
        static(0.5)
        result = make_game3()
        if result:
            say("Congrats on beating the game!")
            game.set("beat_game3")
            game.change("key", +1)
        else:
            say("You didn't beat the game... Good luck with the other ones")
            game.set("lost_game3")
    else:
        say("The machine looks powered off")


def choose_ending(game):
    say("You chose to leave the arcade hall... \nYour fate will be decided...")
    if game.get("key") == 1:
        return "bad"
    if game.get("key") >= 2:
        return "good"
    return "nothing"

    
#  play game functionality
def main_game():
    game = Game("Haunted Arcade",
                start="arcade",
                subtitle="Play the games or suffer the consequences",
                stats={"key": 0})

    game.add(Scene(
        "arcade",
        title="Arcade",
        first_text="You fell asleep in your bed. But when you open your eyes you're at an abandoned arcade hall. There's a door behind you with a poster next to it."
        "\nIn front of you are 3 old arcade machines.",
        text=lambda game: f"{game.get('key')} mini games beaten! \nThere's a door to the west you with a poster next to it."
        "On the other walls are 3 old arcade machines.",
        options=[
            Option("Walk out of the arcade", action=choose_ending),
            # have text show
            Option("Look at the poster", action=read_poster),
            # have each an unique minigame load
            
            Option("Look at machine 1", "machine 1"),
            Option("Look at machine 2", "machine 2"),
            Option("Look at machine 3", "machine 3")
        ],
    ))

    game.add(Scene(
        "machine 1",
        title="Machine 1",
        text="Seems to be a game about luck",
        options=[
            Option("Play the game", action=load_game1),
            Option("Go Back", "arcade")
        ]
    ))

    game.add(Scene(
        "machine 2",
        title="Machine 2",
        text=SNAKE_INTRO,
        options=[
            Option("Play the game", action=load_game2),
            Option("Go Back", "arcade")
        ]
    ))

    game.add(Scene(
        "machine 3",
        title="Machine 3",
        text="Seems to be a game about shooting with apples.",
        options=[
            Option("Play the game", action=load_game3),
            Option("Go Back", "arcade")
        ]
    ))

    game.add(Scene(
        "outside",
        title="Outside",
        text="Cold air. You made it out.[pause] Behind you, the door slowly closes on its own.",
        # check inventory for items for what ending

        ending="win",
    ))

    # endings
    game.add(
    Scene("good", title="Good Gamer", ending="win",
            text=lambda game: f"{game.get('keys')} mini games beaten!"),
    Scene("bad", title="Bad Gamer", ending="lose",
            text=lambda game: f"Only {game.get('keys')} earned..."),
    Scene("nothing", title="Did Nothing", ending="lose",
            text="No games beaten..."),
    )
    return game


if __name__ == "__main__":
    main_game().run()
