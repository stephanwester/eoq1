"""Sounds for the game: your own files, or retro beeps made on the spot."""
from __future__ import annotations

import os
from array import array

import pygame

from tetris.themes import Theme
from textquest.sound import start_mixer

# The beeps: a list of (pitch in Hz, milliseconds) for each event.
BEEPS = {
    "rotate": [(660, 25)],
    "lock": [(200, 40)],
    "hold": [(520, 40), (780, 40)],
    "clear": [(660, 60), (880, 90)],
    "tetris": [(523, 70), (659, 70), (784, 70), (1047, 180)],
    "level": [(784, 60), (988, 60), (1175, 120)],
    "win": [(523, 120), (659, 120), (784, 120), (1047, 320)],
    "lose": [(392, 200), (330, 200), (262, 450)],
}


class Sounds:
    def __init__(self, theme: Theme):
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.on = start_mixer()
        if not self.on:
            return
        for event, path in theme.sounds.items():
            self.sounds[event] = pygame.mixer.Sound(_existing(path))
        if theme.beeps:
            for event, notes in BEEPS.items():
                beep = _make_beep(notes)
                if beep and event not in self.sounds:
                    self.sounds[event] = beep
        if theme.music:
            pygame.mixer.music.load(_existing(theme.music))
            pygame.mixer.music.play(-1)

    def play(self, event: str):
        if event in self.sounds:
            self.sounds[event].play()

    def stop(self):
        if self.on:
            pygame.mixer.music.stop()


def _existing(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"The sound file '{path}' doesn't exist.")
    return path


def _make_beep(notes: list[tuple[int, int]]) -> pygame.mixer.Sound | None:
    """Make a square wave beep, like old game consoles."""
    init = pygame.mixer.get_init()
    if not init or init[1] != -16:  # only 16 bit sound is supported here
        return None
    rate, _, channels = init
    samples = array("h")
    for pitch, ms in notes:
        count = rate * ms // 1000
        period = rate / pitch
        for i in range(count):
            loudness = 2500 * (1 - i / count)  # fade out
            value = int(loudness if i % period < period / 2 else -loudness)
            samples.extend([value] * channels)
    return pygame.mixer.Sound(buffer=samples.tobytes())
