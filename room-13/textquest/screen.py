"""Everything that talks to the terminal goes through a Screen.

The game never prints or reads input directly. That way the tests can swap the
real terminal for a FakeScreen that types its own answers and runs without delays.
"""
import sys
import termios
import time
from contextlib import contextmanager

from blessed import Terminal

# A terminal that always knows the escape codes, even when output is not a real
# terminal. We only use it to check whether a style name like 'red' exists.
_STYLE_CHECKER = Terminal(force_styling=True)


def is_style(name):
    """True if name is something blessed can style text with, like 'red' or 'bold'."""
    return bool(str(getattr(_STYLE_CHECKER, name, "")))


class Screen:
    """The real terminal."""

    def __init__(self):
        self.term = Terminal()

    @property
    def width(self):
        return self.term.width or 80

    @property
    def height(self):
        return self.term.height or 24

    def write(self, text):
        sys.stdout.write(text)
        sys.stdout.flush()

    def style(self, text, styles):
        """Wrap text in the escape codes for the given style names."""
        if not styles or not self.term.does_styling:
            return text
        start = "".join(str(getattr(self.term, name)) for name in styles)
        return start + text + self.term.normal

    def clear(self):
        self.write(self.term.home + self.term.clear)

    def set_colors(self, background, text):
        """Change the colors of the terminal itself. Terminals that can't do this ignore it."""
        if self.term.does_styling:
            self.write(f"\x1b]11;{background}\x07\x1b]10;{text}\x07")

    def reset_colors(self):
        """Give the terminal its own colors back."""
        if self.term.does_styling:
            self.write("\x1b]111\x07\x1b]110\x07")

    def read_line(self, prompt=""):
        try:
            return input(prompt)
        except EOFError:
            return ""

    def sleep(self, seconds):
        time.sleep(seconds)

    @contextmanager
    def typing(self):
        """Use as 'with screen.typing():' so key presses can be noticed while text is typed."""
        if not sys.stdin.isatty():
            yield
            return
        with self.term.cbreak():
            yield
        # Forget keys pressed to skip the typing, so they don't end up in the next answer.
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

    def key_pressed(self):
        """True if the player pressed a key since the last check (does not wait)."""
        if not sys.stdin.isatty():
            return False
        return bool(self.term.inkey(timeout=0))


class FakeScreen:
    """A pretend terminal for tests: answers come from a list, output goes to a string."""

    def __init__(self, answers=(), width=80, height=24):
        self.answers = list(answers)
        self.output = ""
        self.width = width
        self.height = height

    def write(self, text):
        self.output += text

    def style(self, text, styles):
        return text

    def clear(self):
        self.output += "\n[CLEAR]\n"

    def set_colors(self, background, text):
        pass

    def reset_colors(self):
        pass

    def read_line(self, prompt=""):
        self.output += prompt
        if not self.answers:
            raise RuntimeError("FakeScreen ran out of answers. Output so far:\n" + self.output)
        answer = self.answers.pop(0)
        self.output += answer + "\n"
        return answer

    def sleep(self, seconds):
        pass

    def typing(self):
        return _Nothing()

    def key_pressed(self):
        return False


class _Nothing:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


# The screen that all effects use. Tests put a FakeScreen here.
current = Screen()
