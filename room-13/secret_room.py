from textquest.effects import say

SECRET_ROOM_INTRO = """
You step into a small, dusty office.

An old wooden desk stands against the wall.
Papers are scattered across the floor.

On the desk lie 3 coins.
Next to the desk stands a large, locked safe.
On the wall behind it you see 3 posters with strange riddles on it.

A faded family photograph hangs on the wall.

Something about this room feels strangely familiar...
"""

DOCUMENTS = """
Inside the safe are several old documents.

The first is a recent floor plan of the arcade.
You scan it quickly.

Something seems strange...

There is no Room 13.

Underneath it lies an older, faded map.
This one is different.

There it is.

ROOM 13.

Someone has circled it in red ink.

Folded between the maps is an old newspaper clipping.

'ROOM 13 SEALED OFF AFTER MYSTERIOUS INCIDENT'

The rest of the article is too damaged to read clearly,
but a few words still stand out:

'missing child'
'search'
'never found'
"""


def enter_secret_room(game):
    say(SECRET_ROOM_INTRO)
    game.set("secret_explored")


def riddle1(game):
    say("""
    Three silver coins rest on the dusty wooden desk—two to pay the ferryman,
    and one for my cute red bow.
    Count every coin upon the wood.
    """) # antwoord = 3


def riddle2(game):
    say("""
    Five haunted faces stare out from the faded family photograph,
    but one of them wears my red bow and has no mouth to scream.
    Take that silent ghost away,
    and count how many faces remain inside the frame.
    """) # antwoord = 4


def riddle3(game):
    say("""
    I stand beside the locked safe with no mouth to smile,
    staring at you with two dark button eyes beneath my pointed white ears.
    Count my eyes and ears together,
    then cut that number in half—for one of us is only a ghost.
    """) # antwoord = 2


def table(game):
    say("You find a small stash of coins lying on the table.")
    game.change("coins", +3)


def safe_cracking(game):
    user_input = input("Input the 3 digit input of the safe:\n")
    if user_input == "342":
        say("As you put in the code and press enter, the screen lights green.")
        game.set("safe unlocked")
    else:
        say("As you put in the code and press enter, the screen lights [blood]red[/].")
