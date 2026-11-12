from textquest.effects import say


def interact_with_girl(game):

    # Lily has already disappeared
    if game.get("girl_disappeared"):
        say("The corner is empty. Lily is nowhere to be seen.")
        return

    # You already received her key
    if game.get("girl_key"):
        say("""
Lily is still sitting in the corner, hugging her Hello Kitty plushie.

Lily: "Have you seen my mummy yet?"
""")
        return

    say("""
You hear someone crying in a dark corner of the arcade.

A little girl in a faded pink dress sits on the floor,
clutching a dirty Hello Kitty plushie.

Around her neck hangs a small rusty key on a pink ribbon.

Girl: "Excuse me... Have you seen my mummy?"

1. No, sorry. What's your name?
2. Leave her alone.
""")

    choice = input()

    if choice == "2":
        say("You decide to leave the girl alone.")
        return

    # Remember that you talked to Lily
    game.set("talked_to_lily")

    say("""
Girl: "L-Lily... What's your name?"
""")

    name = input("Your name: ")

    say(f"""
Lily: "Oh... {name}. That's a nice name."

She looks down at her plushie.

Lily: "Do you like Hello Kitty?"

1. Yes, I love Hello Kitty!
2. No, not really.
""")

    choice = input()

    if choice == "2":
        say(f"""
Her smile suddenly disappears.

Lily: "You... you don't like Hello Kitty?"

She slowly looks up at you.
Black tears begin rolling down her cheeks.

Lily grabs the key around her neck and holds it tightly.

Lily: "THEN GO AWAY, {name.upper()}!"
""")
        return

    say("""
Lily smiles and hugs her plushie.

Lily: "Really? Me too! Are you lost as well?"

You nod.

Lily: "Oh, how unfortunate! Especially on such a lovely summer day."
Lily: "I wish I could go back outside."

You: "But... it's winter."

Lily looks confused.

Lily: "No, silly! It's summer! Mummy's coming to pick me up soon!"

You: "How long have you been here?"

Her expression goes blank.

Lily: "I... I don't know... I don't... I don't..."

Her head twitches slightly.

Then, just as suddenly, she smiles again.

Lily: "Oh! Did I tell you it's my birthday today?"
Lily: "Mummy gave me Kitty!"

1. Lily... I don't think your mummy is coming back.
2. Happy birthday! I'm sure she'll be here soon.
""")

    choice = input()

    if choice == "1":
        say(f"""
Lily stares at you.

Lily: "No, silly {name}! Mummy promised!"

Her head begins twitching.

Lily: "Silly {name}... silly {name}..."

Her smile grows unnaturally wide.
Black tears slowly roll down her cheeks.

Lily: "No, silly... No, silly..."

Lily: "SILLY {name.upper()}! SILLY {name.upper()}!"

Lily lets out a piercing scream.

For a moment, everything goes dark.

When the lights return, Lily is gone.
The key around her neck has vanished with her.

The arcade falls silent.

Then, from somewhere in the darkness...

Lily: "Silly {name}..."
""")

        # Remember that Lily disappeared
        game.set("girl_disappeared")
        return

    say(f"""
Lily: "Thank you, {name}! I knew she'd come back!"

She giggles and hugs her Hello Kitty plushie.

Lily: "Oh! Did you know there's a secret room behind that closet?"

She proudly holds up the little rusty key hanging around her neck.

Lily: "I found it, so it's mine!"

She looks at you thoughtfully.

Lily: "Hmm... but you can borrow it. I like you, {name}!"

She takes the key off her neck and hands it to you.

Lily: "Promise you'll tell mummy where I am if you see her, okay?"

You obtained the secret room key!
""")

    # Remember that you received the key
    game.set("girl_key")
    return


def open_door(game):

    # Door is already open
    if game.get("door_open"):
        say("The door is already open. You step inside.")
        return "secret room"

    say("""
You notice an old wooden door with a small keyhole.

You try the handle, but it's locked.
""")

    # Player has Lily's key
    if game.get("girl_key"):
        say("""
You take the rusty key Lily gave you and insert it into the lock.

Click.

The door slowly creaks open.

From somewhere behind you, a little girl giggles.

Lily: "Hehe... have fun!"
""")
        game.set("door_open")
        return "secret room"

    # Player has talked to Lily but has no key
    if game.get("talked_to_lily"):
        say("""
From the dark corner of the arcade, you hear a familiar voice.

Lily: "Silly... silly..."

You turn around, but nobody is there.
""")
        return None

    # Player hasn't talked to Lily
    say("""
You look around and notice a little girl sitting in the corner,
holding a Hello Kitty plushie.

A small rusty key hangs around her neck.
""")
    return None
