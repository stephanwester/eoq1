"""Sound. Uses pygame, which also runs the Tetris game."""
import os
from contextlib import contextmanager

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

from textquest.errors import TextQuestError

_problems: list[str] = []  # so the 'sound is off' message is shown only once


def play_sound(path):
    """Play a sound file (.wav or .ogg) without waiting for it to finish."""
    if not os.path.exists(path):
        raise TextQuestError(f"Can't play sound '{path}': there is no such file.")
    if start_mixer():
        pygame.mixer.Sound(path).play()


def start_mixer():
    """Start the sound. Returns False if there's no sound device."""
    if pygame.mixer.get_init():
        return True
    if _problems:
        return False
    try:
        with _no_error_output():
            pygame.mixer.init()
    except pygame.error:
        print("(Sound is off: no sound device was found. On WSL, run: sudo apt install libpulse0)")
        _problems.append("no sound device")
        return False
    return True


@contextmanager
def _no_error_output():
    """Hide the long list of errors that the sound drivers print when they find no device."""
    errors = os.dup(2)
    nowhere = os.open(os.devnull, os.O_WRONLY)
    os.dup2(nowhere, 2)
    try:
        yield
    finally:
        os.dup2(errors, 2)
        os.close(errors)
        os.close(nowhere)
