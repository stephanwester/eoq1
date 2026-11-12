"""The rules of the game. Nothing in here draws: that's window.py.

Your own functions (on_start, on_lock, on_clear, on_second, keys and a piece's
on_lock) always get the game. They can read and change it:

    def check_goal(game):
        if game.lines >= 10:
            game.end(won=True)
"""
from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tetris.pieces import CLASSIC, Cells, Color, Piece, find_piece, rotate
from tetris.window import run_window

if TYPE_CHECKING:
    from tetris.themes import Theme

GameFunction = Callable[["Tetris"], None]

POINTS = [0, 100, 300, 500, 800, 1200]  # for clearing 0, 1, 2, 3, 4 or 5 lines at once


@dataclass
class Block:
    """One square that has landed."""
    color: Color
    name: str                 # the piece it came from
    image: str | None = None


class Tetris:
    def __init__(
        self,
        *,
        title: str = "TETRIS",
        message: str = "",
        theme: str | Theme = "spooky",
        columns: int = 10,
        rows: int = 20,
        pieces: list[Piece] | None = None,
        level: int = 1,
        lines_per_level: int | None = 10,
        hold: bool = True,
        ghost: bool = True,
        preview: int = 3,
        info: dict | None = None,
        on_start: GameFunction | None = None,
        on_lock: GameFunction | None = None,
        on_clear: GameFunction | None = None,
        on_second: GameFunction | None = None,
        keys: dict[str, GameFunction] | None = None,
        intro: bool = True,
        seed: int | None = None,
    ):
        self.title = title
        self.message = message
        self.theme = theme
        self.columns = columns
        self.rows = rows
        self.pieces = pieces if pieces is not None else CLASSIC
        if not self.pieces:
            raise ValueError("pieces is empty. Give at least one piece, or leave it out for the classic ones.")
        self.level = level
        self.start_level = level
        self.lines_per_level = lines_per_level
        self.gravity = True                # False: pieces only fall when the player pushes them
        self.hold_enabled = hold
        self.ghost = ghost
        self.preview = preview
        self.info = dict(info or {})
        self.on_start = on_start
        self.on_lock = on_lock
        self.on_clear = on_clear
        self.on_second = on_second
        self.keys = dict(keys or {})   # {"b": use_bomb}: pressing B runs use_bomb(game)
        self.intro = intro
        self.random = random.Random(seed)

        # The board: (column, row) -> Block. Row 0 is the top.
        self.blocks: dict[tuple[int, int], Block] = {}

        self.score = 0
        self.lines = 0
        self.time = 0.0
        self.pieces_used = 0
        self.over = False
        self.won = False
        self.quit = False
        self.held: Piece | None = None
        self.can_hold = True
        self.landed: Cells = []            # where the last piece landed
        self.just_cleared = 0              # lines cleared by the last piece
        self.just_cleared_blocks: list[str] = []  # names of the pieces those blocks came from
        self.cleared: dict[str, int] = {}  # all cleared blocks, counted per piece name

        # For the window: messages, effects and sounds to play.
        self.messages: list[list] = []     # [text, seconds left]
        self.shaking = 0.0
        self.shake_strength = 6
        self.flashing = 0.0
        self.flash_color: Color = "white"
        self.dark = 0.0
        self.events: list[str] = []

        self.queue: list[Piece] = []       # the next pieces
        self.piece: Piece = self.pieces[0]  # the falling piece, chosen in start()
        self.cells: Cells = []
        self.x = 0
        self.y = 0
        self._fall_timer = 0.0
        self._next_second = 1

    # ---------- things your functions can use ----------

    def say(self, text: str, seconds: float = 2.0):
        """Show a message on top of the board for a moment."""
        self.messages.append([text, seconds])
        self.messages = self.messages[-3:]

    def shake(self, seconds: float = 0.3, strength: int = 6):
        """Shake the board."""
        self.shaking = seconds
        self.shake_strength = strength

    def flash(self, color: Color = "white", seconds: float = 0.15):
        """Flash the screen in a color."""
        self.flash_color = color
        self.flashing = seconds

    def lights_out(self, seconds: float = 3.0):
        """Turn the lights off: only the falling piece can be seen. Spooky."""
        self.dark = seconds

    def add_block(self, x: int, y: int, color: Color = "gray", name: str = "block"):
        """Put a block on the board. (0, 0) is the top left."""
        self.blocks[(x, y)] = Block(color, name)

    def remove_block(self, x: int, y: int):
        self.blocks.pop((x, y), None)

    def set_next(self, piece: str | Piece):
        """Choose the next piece, by name or as a Piece. Call it again to put another one in front."""
        if isinstance(piece, str):
            piece = find_piece(piece, self.pieces)
        self.queue.insert(0, piece)

    def end(self, won: bool = True):
        """Stop the game."""
        if self.over:
            return
        self.over = True
        self.won = won
        self.events.append("win" if won else "lose")

    def result(self) -> dict:
        """What play() gives back when the game is over."""
        return {
            "won": self.won,
            "score": self.score,
            "lines": self.lines,
            "level": self.level,
            "time": round(self.time, 1),
            "pieces": self.pieces_used,
            "quit": self.quit,
            "cleared": dict(self.cleared),
            "info": dict(self.info),
        }

    def play(self) -> dict:
        """Open a window, play until the game is over and return the result."""
        self.start()
        run_window(self)
        return self.result()

    def start(self):
        """Run your on_start function, then drop the first piece."""
        if self.on_start:
            self.on_start(self)
        self._next_piece()

    # ---------- the player's moves (the window calls these) ----------

    def move(self, dx: int, dy: int = 0) -> bool:
        if self.over or not self.fits(self.cells, self.x + dx, self.y + dy):
            return False
        self.x += dx
        self.y += dy
        return True

    def rotate(self, clockwise: bool = True):
        if self.over or not self.piece.can_rotate:
            return
        turned = rotate(self.cells, clockwise)
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]:
            if self.fits(turned, self.x + dx, self.y + dy):
                self.cells = turned
                self.x += dx
                self.y += dy
                self.events.append("rotate")
                return

    def soft_drop(self):
        if self.move(0, 1):
            self.score += 1
            self._fall_timer = 0.0
        elif not self.over:
            self._lock()

    def hard_drop(self):
        if self.over:
            return
        while self.move(0, 1):
            self.score += 2
        self._lock()

    def hold(self):
        if self.over or not self.hold_enabled or not self.can_hold:
            return
        if self.held is None:
            self.held = self.piece
            self._next_piece()
        else:
            self.held, piece = self.piece, self.held
            self._spawn(piece)
        self.can_hold = False
        self.events.append("hold")

    def update(self, seconds: float):
        """Let time pass: gravity, timers and your on_second function."""
        if self.over:
            return
        self.time += seconds
        while self.time >= self._next_second and not self.over:
            self._next_second += 1
            if self.on_second:
                self.on_second(self)
        if self.over:
            return

        self._fall_timer += seconds
        if self.gravity and self._fall_timer >= self.fall_delay:
            self._fall_timer = 0.0
            if not self.move(0, 1):
                self._lock()

        for message in self.messages:
            message[1] -= seconds
        self.messages = [m for m in self.messages if m[1] > 0]
        self.shaking = max(0.0, self.shaking - seconds)
        self.flashing = max(0.0, self.flashing - seconds)
        self.dark = max(0.0, self.dark - seconds)

    # ---------- questions about the game ----------

    @property
    def fall_delay(self) -> float:
        """Seconds between falls. Goes down as the level goes up."""
        return max(0.05, 0.8 * 0.85 ** (self.level - 1))

    def fits(self, cells: Cells, x: int, y: int) -> bool:
        """True if the cells fit on the board at (x, y). Above the top is allowed."""
        for cx, cy in cells:
            column, row = x + cx, y + cy
            if column < 0 or column >= self.columns or row >= self.rows:
                return False
            if (column, row) in self.blocks:
                return False
        return True

    def ghost_y(self) -> int:
        """The row the falling piece would land on."""
        y = self.y
        while self.fits(self.cells, self.x, y + 1):
            y += 1
        return y

    # ---------- inside the rules ----------

    def _next_piece(self):
        """Take the next piece from the queue, and pick new random pieces for the queue."""
        weights = [p.weight for p in self.pieces]
        while len(self.queue) < self.preview + 1:
            self.queue.append(self.random.choices(self.pieces, weights)[0])
        self._spawn(self.queue.pop(0))

    def _spawn(self, piece: Piece):
        self.piece = piece
        self.cells = list(piece.cells)
        self.x = (self.columns - 1) // 2
        self.y = -min(y for _, y in self.cells)
        self._fall_timer = 0.0
        if not self.fits(self.cells, self.x, self.y):
            self.end(won=False)

    def _lock(self):
        self.landed = [(self.x + cx, self.y + cy) for cx, cy in self.cells]
        for position in self.landed:
            self.blocks[position] = Block(self.piece.color, self.piece.name, self.piece.image)
        self.pieces_used += 1
        self.can_hold = True
        self.events.append("lock")
        if any(y < 0 for _, y in self.landed):
            self.end(won=False)
            return

        if self.piece.on_lock:
            self.piece.on_lock(self)
        if self.on_lock and not self.over:
            self.on_lock(self)
        if self.over:
            return

        self._clear_full_rows()
        if not self.over:
            self._next_piece()

    def _clear_full_rows(self):
        full = [row for row in range(self.rows)
                if all((column, row) in self.blocks for column in range(self.columns))]
        self.just_cleared = len(full)
        self.just_cleared_blocks = [self.blocks[(column, row)].name for row in full for column in range(self.columns)]
        if not full:
            return

        for name in self.just_cleared_blocks:
            self.cleared[name] = self.cleared.get(name, 0) + 1
        new_blocks = {}
        for (column, row), block in self.blocks.items():
            if row not in full:
                drop = sum(1 for full_row in full if full_row > row)
                new_blocks[(column, row + drop)] = block
        self.blocks = new_blocks

        self.lines += len(full)
        self.score += POINTS[min(len(full), len(POINTS) - 1)] * self.level
        if len(full) >= 4:
            self.say("TETRIS!")
            self.shake()
            self.events.append("tetris")
        else:
            self.events.append("clear")
        if self.lines_per_level:
            new_level = self.start_level + self.lines // self.lines_per_level
            if new_level > self.level:
                self.level = new_level
                self.say(f"LEVEL {self.level}")
                self.events.append("level")
        if self.on_clear:
            self.on_clear(self)
