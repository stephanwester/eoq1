"""Reads [tags] in text, like "[red]blood[/]" or "Wait...[pause=2] there!".

parse() turns a string into a list of pieces. A piece is either some text with
its styles, or a pause.
"""
import re
from dataclasses import dataclass

from textquest.screen import is_style

# Speed tags change how fast the typewriter types. The number is a multiplier
# for the delay between letters: bigger is slower, 0 is instant.
SPEEDS = {"slow": 4.0, "fast": 0.3, "instant": 0.0}

# Effect tags change how text appears.
EFFECTS = {"glitch"}

# Short names for a few tags together. Add your own here.
MOODS = {"whisper": "dim italic slow", "blood": "bold red"}

# Matches "[[" (a literal bracket), "[name]", "[bold red]", "[name=2]", "[/name]" and "[/]".
TAG = re.compile(r"\[\[|\[(/?)([a-z_ ]*)(?:=([0-9.]+))?\]")


@dataclass
class Piece:
    kind: str                # "text" or "pause"
    text: str = ""
    styles: tuple = ()
    speed: float = 1.0
    effect: str = ""
    seconds: float = 0.0


def is_tag(name):
    if name in SPEEDS or name in EFFECTS or name in MOODS:
        return True
    # A style tag can hold several styles: "[bold red]".
    return bool(name.split()) and all(is_style(style) for style in name.split())


def parse(text):
    pieces = []
    open_tags = []

    def add_text(chunk):
        if chunk:
            pieces.append(_text_piece(chunk, open_tags))

    pos = 0
    for match in TAG.finditer(text):
        add_text(text[pos:match.start()])
        pos = match.end()
        closing, name, value = match.groups()

        if match.group(0) == "[[":
            add_text("[")
        elif closing:
            _close(open_tags, name)
        elif name == "pause":
            pieces.append(Piece("pause", seconds=float(value) if value else 1.0))
        elif is_tag(name):
            open_tags.append(name)
        else:
            # Not a tag we know, like "[1]" or a typo: just show it as text.
            add_text(match.group(0))

    add_text(text[pos:])
    return pieces


def _text_piece(chunk, open_tags):
    """A piece of text, styled by the tags that are open."""
    names = [word for t in open_tags for word in MOODS.get(t, t).split()]
    styles = tuple(name for name in names if name not in SPEEDS and name not in EFFECTS)
    speed = 1.0
    for name in names:
        if name in SPEEDS:
            speed = SPEEDS[name]
    effect = next((name for name in reversed(names) if name in EFFECTS), "")
    return Piece("text", chunk, styles, speed, effect)


def _close(open_tags, name):
    """"[/]" closes the last tag, "[/red]" closes the last 'red' tag."""
    if name and name in open_tags:
        index = len(open_tags) - 1 - open_tags[::-1].index(name)
        del open_tags[index]
    elif not name and open_tags:
        open_tags.pop()


def plain(text):
    """The text without any tags."""
    return "".join(p.text for p in parse(text) if p.kind == "text")


def wrap(pieces, width):
    """Split text pieces so no line is wider than width, breaking only at spaces."""
    # Work on single letters so a word can be measured across pieces.
    letters = []
    for piece in pieces:
        if piece.kind == "text":
            letters += [(ch, piece) for ch in piece.text]
        else:
            letters.append((None, piece))

    column = 0
    for i, (ch, piece) in enumerate(letters):
        if ch is None:
            continue
        if ch == "\n":
            column = 0
        elif ch == " " and column > 0 and column + 1 + _next_word_length(letters, i + 1) > width:
            letters[i] = ("\n", piece)
            column = 0
        else:
            column += 1
    return _glue(letters)


def _next_word_length(letters, start):
    length = 0
    for ch, _ in letters[start:]:
        if ch is None:
            continue
        if ch in " \n":
            break
        length += 1
    return length


def _glue(letters):
    """Glue letters back together into pieces."""
    result = []
    for ch, piece in letters:
        if ch is None:
            result.append(piece)
        elif result and result[-1].kind == "text" and result[-1].styles == piece.styles \
                and result[-1].speed == piece.speed and result[-1].effect == piece.effect:
            result[-1].text += ch
        else:
            result.append(Piece("text", ch, piece.styles, piece.speed, piece.effect))
    return result
