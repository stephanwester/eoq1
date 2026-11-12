"""Pieces: the shapes that fall.

Draw a piece with # for a block and . for empty space:

    CROSS = Piece("cross", '''
        .#.
        ###
        .#.
    ''', "red")

Colors can be names ("red", "orange", "hotpink"), "#ff8800" or (255, 136, 0).
"""
from __future__ import annotations

import textwrap
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tetris.game import Tetris

Color = str | tuple[int, int, int]
Cells = list[tuple[int, int]]


@dataclass
class Piece:
    name: str
    shape: str
    color: Color = "white"
    weight: float = 1.0            # 2.0 = shows up twice as often, 0.5 = half as often
    image: str | None = None       # a picture file to draw on every block of this piece
    on_lock: Callable[[Tetris], None] | None = None   # runs when this piece lands
    cells: Cells = field(init=False)

    def __post_init__(self):
        self.cells = cells_from_drawing(self.shape, self.name)

    @property
    def can_rotate(self):
        """False for shapes that look the same after turning, like the O piece."""
        return _normalized(rotate(self.cells)) != _normalized(self.cells)


def cells_from_drawing(drawing: str, name: str = "?") -> Cells:
    """Turn a drawing into (x, y) cells around the middle of the piece."""
    lines = textwrap.dedent(drawing).strip("\n").splitlines()
    filled = [(x, y) for y, line in enumerate(lines) for x, ch in enumerate(line) if ch not in ". "]
    if not filled:
        raise ValueError(f"Piece '{name}' has no blocks. Use # for blocks and . for empty space.")
    xs = [x for x, _ in filled]
    ys = [y for _, y in filled]
    middle_x = (min(xs) + max(xs)) // 2
    middle_y = (min(ys) + max(ys) + 1) // 2
    return [(x - middle_x, y - middle_y) for x, y in filled]


def rotate(cells: Cells, clockwise: bool = True) -> Cells:
    """Turn cells a quarter turn. y goes down on the screen, so (x, y) becomes (-y, x)."""
    if clockwise:
        return [(-y, x) for x, y in cells]
    return [(y, -x) for x, y in cells]


def _normalized(cells: Cells):
    left = min(x for x, _ in cells)
    top = min(y for _, y in cells)
    return sorted((x - left, y - top) for x, y in cells)


# ---------- the seven classic pieces ----------

CLASSIC = [
    Piece("I", "####", "cyan"),
    Piece("O", "##\n##", "yellow"),
    Piece("T", ".#.\n###", "purple"),
    Piece("S", ".##\n##.", "green"),
    Piece("Z", "##.\n.##", "red"),
    Piece("J", "#..\n###", "blue"),
    Piece("L", "..#\n###", "orange"),
]


def find_piece(name: str, pieces: list[Piece]) -> Piece:
    """Find a piece by name, with a clear message if it's not there."""
    for piece in pieces:
        if piece.name == name:
            return piece
    names = ", ".join(p.name for p in pieces)
    raise ValueError(f"There is no piece called '{name}'. The pieces are: {names}.")
