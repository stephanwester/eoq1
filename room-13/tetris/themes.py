"""Themes: how the game looks and sounds.

Use a theme by name:            Tetris(theme="retro")
Change a few things of one:     Tetris(theme=THEMES["spooky"].change(block_style="round"))
Or make your own from scratch:  Tetris(theme=Theme(background="black", board="darkred"))
"""
from __future__ import annotations

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass, field

from tetris.pieces import Color


@dataclass
class Theme:
    background: Color = (6, 6, 12)
    board: Color = (8, 8, 16)
    grid: Color | None = (22, 22, 35)     # None = no grid lines
    border: Color = (140, 140, 255)
    text: Color = (180, 180, 230)
    title: Color = (200, 200, 255)
    block_style: str | Callable = "glow"  # glow, classic, flat, round, outline, pixel or your own function
    bloom: bool = True                    # blocks give off light
    flicker: bool = False                 # the lights fail now and then
    font: str | None = None               # a font file (.ttf) or the name of a font on your computer
    background_image: str | None = None
    piece_colors: dict[str, Color] = field(default_factory=dict)  # {"T": "hotpink"} changes a piece's color
    sounds: dict[str, str] = field(default_factory=dict)          # {"clear": "boom.wav"}, see SOUND_EVENTS
    beeps: bool = True                    # retro beeps for events that have no sound file
    music: str | None = None              # a music file that loops while you play

    def change(self, **changes) -> Theme:
        """A copy of this theme with some things changed."""
        return dataclasses.replace(self, **changes)


SOUND_EVENTS = ["rotate", "lock", "hold", "clear", "tetris", "level", "win", "lose"]

THEMES = {
    "neon": Theme(),
    "retro": Theme(
        background="black", board="black", grid=None, border="white", text="white", title="white",
        block_style="classic", bloom=False,
    ),
    "spooky": Theme(
        background=(10, 5, 6), board=(16, 8, 9), grid=(38, 18, 20), border=(170, 16, 28),
        text=(216, 208, 196), title=(215, 20, 34), flicker=True,
        piece_colors={
            "I": "#d8d0c4", "O": "#c9a227", "T": "#7d4a8c", "S": "#5f7f5a",
            "Z": "#d41420", "J": "#44657a", "L": "#b5602a",
        },
    ),
    "dungeon": Theme(
        background=(20, 18, 16), board=(32, 29, 26), grid=(44, 40, 36), border=(150, 130, 100),
        text=(220, 200, 160), title=(230, 180, 60), block_style="classic", bloom=False,
        piece_colors={
            "I": (90, 140, 160), "O": (200, 170, 80), "T": (130, 90, 150), "S": (100, 140, 80),
            "Z": (160, 70, 60), "J": (70, 90, 140), "L": (180, 110, 60),
        },
    ),
}


def get_theme(theme: str | Theme) -> Theme:
    if isinstance(theme, Theme):
        return theme
    if theme not in THEMES:
        raise ValueError(f"There is no theme called '{theme}'. Pick one of: {', '.join(THEMES)}.")
    return THEMES[theme]
