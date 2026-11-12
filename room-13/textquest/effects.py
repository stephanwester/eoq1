"""Functions for showing text to the player and asking them things.

Use say() for everything you show. It understands tags:
    say("The door creaks open...[pause] [red]something[/] is inside.")
"""
import random

from textquest import markup, screen
from textquest.sound import play_sound

settings = {
    "text_speed": 0.03,  # seconds per letter, 0 shows text at once
    "max_width": 80,     # text wraps at this many letters (or less if the window is smaller)
}

GLITCH_LETTERS = "#%&@$!?*<>/\\|~^"
STATIC_LETTERS = " ░▒▓"

SCARY_FACE = r"""
         .-''-.
       .'  __    __  '.
      /   /  \  /  \   \
     |    \__/  \__/    |
     |       /\         |
      \   .-'-.  /
       '. |VVVVVVVVV| .'
         '|AAAAAAAAA|'
          '---------'
"""


def say(text="", speed=None, end="\n"):
    """Show text like a typewriter. The player can press any key to show the rest at once."""
    s = screen.current
    delay = settings["text_speed"] if speed is None else speed
    width = min(s.width, settings["max_width"])
    pieces = markup.wrap(markup.parse(str(text)), width)

    skipping = False
    with s.typing():
        for piece in pieces:
            if piece.kind == "pause":
                if not skipping:
                    skipping = _wait(s, piece.seconds)
                continue

            per_letter = delay * piece.speed
            if skipping or per_letter == 0:
                s.write(s.style(piece.text, piece.styles))
                continue

            for i, ch in enumerate(piece.text):
                if piece.effect == "glitch" and not ch.isspace():
                    for _ in range(2):
                        s.write(s.style(random.choice(GLITCH_LETTERS), piece.styles) + "\b")
                        s.sleep(per_letter)
                s.write(s.style(ch, piece.styles))
                if ch != "\n":
                    s.sleep(per_letter)
                if s.key_pressed():
                    skipping = True
                    s.write(s.style(piece.text[i + 1:], piece.styles))
                    break
    s.write(end)


def _wait(s, seconds):
    """Wait, but stop early when a key is pressed. Returns True if a key was pressed."""
    waited = 0.0
    while waited < seconds:
        s.sleep(0.05)
        waited += 0.05
        if s.key_pressed():
            return True
    return False


def wait(seconds=1.0):
    """Do nothing for a moment. Good for tension."""
    screen.current.sleep(seconds)


def wait_for_key(seconds):
    """Wait a few seconds for a key press. True if a key was pressed, False if time ran out."""
    s = screen.current
    with s.typing():
        return _wait(s, seconds)


def clear():
    """Clear the screen."""
    screen.current.clear()


def pause(prompt="Press Enter to continue..."):
    """Wait until the player presses Enter."""
    s = screen.current
    s.read_line(s.style(prompt, ("dim",)))


def ask(question):
    """Ask the player to type something. Returns what they typed."""
    say(question)
    return screen.current.read_line("> ").strip()


def choose(question, choices):
    """Let the player pick one of the choices. Returns the choice they picked.

        door = choose("Which door?", ["Left", "Right"])
    """
    say(question)
    for number, choice in enumerate(choices, start=1):
        say(f"  {number}. {choice}", speed=0)
    while True:
        answer = screen.current.read_line("> ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            return choices[int(answer) - 1]
        for choice in choices:
            if answer.lower() == str(choice).lower():
                return choice
        say(f"[red]Type a number from 1 to {len(choices)}.[/]", speed=0)


def colored(text, color="cyan"):
    """Put color tags around text, for use inside say(): say("A " + colored("ghost", "white") + "!")"""
    return f"[{color}]{text}[/]"


def boxed(text, color=None):
    """Put a box around text. Returns the text, so show it with say()."""
    lines = str(text).splitlines() or [""]
    width = max(len(markup.plain(line)) for line in lines)
    top = "╔" + "═" * (width + 2) + "╗"
    bottom = "╚" + "═" * (width + 2) + "╝"
    middle = ["║ " + line + " " * (width - len(markup.plain(line))) + " ║" for line in lines]
    box = "\n".join([top] + middle + [bottom])
    return colored(box, color) if color else box


def show_art(art, color=None):
    """Show ASCII art at once, exactly as you drew it (tags are not read here)."""
    s = screen.current
    for line in art.strip("\n").splitlines():
        s.write(s.style(line, (color,) if color else ()) + "\n")


def drips(width):
    """Two lines of blood to put under a box of this width."""
    top = [" "] * width
    bottom = [" "] * width
    for x in random.sample(range(1, width - 1), max(2, width // 3)):
        top[x] = "│"
        if random.random() < 0.5:
            bottom[x] = "╵"
    return "".join(top) + "\n" + "".join(bottom)


def flicker(times=2):
    """Make the whole screen flash, like the lights are failing.

    Don't make this much faster: more than 3 flashes per second can be dangerous
    for people with epilepsy.
    """
    s = screen.current
    for _ in range(times):
        s.write("\x1b[?5h")  # screen colors reversed
        s.sleep(0.2)
        s.write("\x1b[?5l")  # back to normal
        s.sleep(0.5)


def static(seconds=1.0):
    """Fill the screen with TV noise for a moment."""
    s = screen.current
    for _ in range(int(seconds / 0.06)):
        noise = ["".join(random.choices(STATIC_LETTERS, k=s.width)) for _ in range(s.height - 1)]
        s.write("\x1b[H" + s.style("\n".join(noise), ("dim",)))  # \x1b[H goes to the top left
        s.sleep(0.06)
    s.clear()


def jumpscare(art=SCARY_FACE, sound=None):
    """Clear the screen and show something scary, with one flash. Use it rarely!"""
    s = screen.current
    s.clear()
    if sound:
        play_sound(sound)
    show_art(art, "bold_red")
    flicker(1)
    s.sleep(0.8)
    s.clear()
