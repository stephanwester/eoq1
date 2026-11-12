"""The window: draws the game and reads the keyboard. The rules are in game.py."""
from __future__ import annotations

import os
import random
from collections.abc import Callable
from typing import TYPE_CHECKING

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

from tetris.pieces import Color, Piece
from tetris.sounds import Sounds
from tetris.themes import get_theme

if TYPE_CHECKING:
    from tetris.game import Tetris

AnyColor = Color | pygame.Color

# Which keys do what. Import KEYS in your own code to change them (see Controls in the README).
KEYS = {
    "left": [pygame.K_LEFT, pygame.K_a],
    "right": [pygame.K_RIGHT, pygame.K_d],
    "down": [pygame.K_DOWN, pygame.K_s],
    "rotate": [pygame.K_UP, pygame.K_w, pygame.K_x],
    "rotate_back": [pygame.K_z, pygame.K_q],
    "drop": [pygame.K_SPACE],
    "hold": [pygame.K_c, pygame.K_LSHIFT, pygame.K_RSHIFT],
    "pause": [pygame.K_p],
    "quit": [pygame.K_ESCAPE],
}

ACTIONS: dict[str, Callable[[Tetris], object]] = {
    "left": lambda game: game.move(-1),
    "right": lambda game: game.move(1),
    "down": lambda game: game.soft_drop(),
    "rotate": lambda game: game.rotate(),
    "rotate_back": lambda game: game.rotate(clockwise=False),
    "drop": lambda game: game.hard_drop(),
    "hold": lambda game: game.hold(),
}
REPEATING = {"left", "right", "down"}  # holding these keys down repeats them

CONTROLS = [
    "LEFT / RIGHT   move",
    "UP             rotate",
    "Z              rotate back",
    "DOWN           fall faster",
    "SPACE          drop",
    "C              hold",
    "P              pause",
    "ESC            give up",
]

FPS = 60


def run_window(game: Tetris):
    """Play the game in a window until it's over."""
    pygame.display.init()
    pygame.font.init()
    window = Window(game)
    try:
        if game.intro and not window.wait_for_enter(window.draw_intro):
            game.quit = True
            game.end(won=False)
            return
        window.play()
        if not game.quit:
            pygame.time.wait(400)  # so a held key doesn't skip the end screen
            pygame.event.clear()
            window.wait_for_enter(window.draw_end)
    finally:
        window.sounds.stop()
        pygame.display.quit()


class Window:
    def __init__(self, game: Tetris):
        self.game = game
        self.theme = get_theme(game.theme)
        _check_theme(game, self.theme.block_style)

        self.cell = max(12, min(30, 600 // game.rows, 840 // game.columns))  # fits on a laptop screen
        self.small_cell = max(10, self.cell * 2 // 3)
        panel = max(180, self.small_cell * 6 + 40)
        board_width = game.columns * self.cell
        width = max(640, board_width + 2 * panel + 80)
        height = max(480, 90 + game.rows * self.cell + 30)
        self.board = pygame.Rect((width - board_width) // 2, 90, board_width, game.rows * self.cell)
        self.left_x = self.board.left - panel - 20
        self.right_x = self.board.right + 30

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(game.title)
        pygame.key.set_repeat(170, 50)
        self.glow = pygame.Surface((width, height))
        self.images: dict[str, pygame.Surface] = {}
        self.background = self._load_background()
        self.fonts = {size: self._font(size) for size in (18, 24, 36, 48)}
        self.sounds = Sounds(self.theme)
        self.paused = False
        self.flicker_left = 0.0

    # ---------- the loop ----------

    def play(self):
        game = self.game
        clock = pygame.time.Clock()
        held_keys = set()
        while not game.over:
            seconds = clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.quit = True
                    game.end(won=False)
                elif event.type == pygame.KEYUP:
                    held_keys.discard(event.key)
                elif event.type == pygame.KEYDOWN:
                    first_press = event.key not in held_keys
                    held_keys.add(event.key)
                    self.press(event.key, first_press)
            if not self.paused:
                game.update(seconds)
                self._update_flicker(seconds)
            for name in game.events:
                self.sounds.play(name)
            game.events.clear()
            self.draw()
            pygame.display.flip()

    def press(self, key: int, first_press: bool):
        game = self.game
        action = next((name for name, keys in KEYS.items() if key in keys), None)
        own_function = game.keys.get(pygame.key.name(key))
        if action == "quit":
            game.quit = True
            game.end(won=False)
        elif action == "pause" and first_press:
            self.paused = not self.paused
        elif self.paused or game.over:
            return
        elif own_function:
            if first_press:
                own_function(game)
        elif action in ACTIONS and (first_press or action in REPEATING):
            ACTIONS[action](game)

    def wait_for_enter(self, draw_overlay: Callable[[], None]) -> bool:
        """Show a screen until Enter is pressed. Returns False if the player closed the window."""
        clock = pygame.time.Clock()
        while True:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key in {pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE}:
                        return True
                    if event.key in KEYS["quit"]:
                        return False
            self.draw()
            draw_overlay()
            pygame.display.flip()

    # ---------- drawing ----------

    def draw(self):
        """Draw one frame, from back to front."""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.theme.background)
        self._text(self.game.title, 48, self.theme.title, (self.screen.get_width() // 2, 45), center=True)

        board = self.board
        if self.game.shaking:
            strength = self.game.shake_strength
            board = board.move(random.randint(-strength, strength), random.randint(-strength, strength))
        self._draw_board(board)
        self._draw_blocks(board)
        self._draw_panels()
        self._draw_messages(board)
        self._draw_effects()

    def _draw_board(self, board: pygame.Rect):
        game, theme = self.game, self.theme
        pygame.draw.rect(self.screen, theme.board, board)
        for thickness, amount in [(5, 0.75), (3, 0.5), (1, 0.0)]:
            border = pygame.Color(theme.border).lerp(theme.background, amount)
            pygame.draw.rect(self.screen, border, board.inflate(thickness * 2, thickness * 2), thickness)
        if not theme.grid:
            return
        for column in range(game.columns + 1):
            x = board.left + column * self.cell
            pygame.draw.line(self.screen, theme.grid, (x, board.top), (x, board.bottom - 1))
        for row in range(game.rows + 1):
            y = board.top + row * self.cell
            pygame.draw.line(self.screen, theme.grid, (board.left, y), (board.right - 1, y))

    def _draw_blocks(self, board: pygame.Rect):
        """The blocks on the board, the falling piece and its ghost."""
        game = self.game
        squares = []  # (x, y, color, image) for every block to draw
        if not game.dark:
            squares += [(x, y, self._color_of(b.name, b.color), b.image) for (x, y), b in game.blocks.items()]
        if not game.over:
            color = self._color_of(game.piece.name, game.piece.color)
            if game.ghost and not game.dark:
                self._draw_ghost(board, color)
            squares += [(game.x + cx, game.y + cy, color, game.piece.image) for cx, cy in game.cells]

        if self.theme.bloom:
            self.glow.fill("black")
        for x, y, color, image in squares:
            rect = self._cell_rect(board, x, y)
            if rect:
                self._block(self.screen, rect, color, image)
                if self.theme.bloom:
                    self._block(self.glow, rect, pygame.Color(color).lerp("black", 0.4), None)
        if self.theme.bloom:
            self._add_bloom()

    def _draw_ghost(self, board: pygame.Rect, color: Color):
        """An outline where the falling piece will land."""
        game = self.game
        ghost_y = game.ghost_y()
        ghost_color = pygame.Color(color).lerp(self.theme.board, 0.5)
        for cx, cy in game.cells:
            rect = self._cell_rect(board, game.x + cx, ghost_y + cy)
            if rect:
                pygame.draw.rect(self.screen, ghost_color, rect.inflate(-2, -2), 2)

    def _draw_panels(self):
        """HOLD and info on the left, NEXT and the numbers on the right."""
        game, theme = self.game, self.theme
        top = self.board.top
        if game.hold_enabled:
            self._text("HOLD", 24, theme.title, (self.left_x, top))
            if game.held:
                self._mini_piece(game.held, self.left_x, top + 40)
            top += 40 + 4 * self.small_cell
        for name, value in game.info.items():
            self._text(f"{str(name).upper()} {value}", 24, theme.text, (self.left_x, top))
            top += 32

        top = self.board.top
        if game.preview:
            self._text("NEXT", 24, theme.title, (self.right_x, top))
            top += 40
            for piece in game.queue[:game.preview]:
                top += self._mini_piece(piece, self.right_x, top) + self.small_cell
        top = max(top, self.board.top + 200) + 10

        lines = [f"SCORE {game.score}", f"LINES {game.lines}", f"LEVEL {game.level}", f"TIME  {int(game.time)}"]
        for text in lines:
            self._text(text, 24, theme.text, (self.right_x, top))
            top += 30

    def _draw_messages(self, board: pygame.Rect):
        for index, (text, _) in enumerate(self.game.messages):
            position = (board.centerx, board.top + board.height // 3 + index * 44)
            self._text(text, 36, self.theme.title, position, center=True)

    def _draw_effects(self):
        everything = self.screen.get_rect()
        if self.flicker_left:
            self._shade(everything, "black", 150)
        if self.game.flashing:
            self._shade(everything, self.game.flash_color, int(min(1.0, self.game.flashing / 0.15) * 140))
        if self.paused:
            self._shade(self.board, "black", 180)
            self._text("PAUSED", 36, self.theme.title, self.board.center, center=True)

    def draw_intro(self):
        game, theme = self.game, self.theme
        self._shade(self.screen.get_rect(), "black", 225)
        x = self.screen.get_width() // 2
        y = 130
        for line in _wrap(game.message, 36):
            self._text(line, 24, theme.text, (x, y), center=True)
            y += 30
        y += 40
        controls = CONTROLS + [f"{key.upper():<15}{function.__name__.replace('_', ' ')}"
                               for key, function in game.keys.items()]
        for line in controls:
            self._text(line, 18, theme.text, (x - 110, y))
            y += 24
        self._text("Press ENTER to start", 24, theme.title, (x, y + 30), center=True)

    def draw_end(self):
        game, theme = self.game, self.theme
        self._shade(self.screen.get_rect(), "black", 170)
        x, y = self.screen.get_width() // 2, self.screen.get_height() // 2
        self._text("YOU SURVIVED" if game.won else "IT GOT YOU", 48, theme.title, (x, y - 60), center=True)
        self._text(f"Score {game.score}", 36, theme.text, (x, y), center=True)
        self._text("Press ENTER", 24, theme.text, (x, y + 60), center=True)

    # ---------- blocks ----------

    def _mini_piece(self, piece: Piece, left: int, top: int) -> int:
        """Draw a small piece for HOLD and NEXT. Returns how tall it is."""
        size = self.small_cell
        min_x = min(x for x, _ in piece.cells)
        min_y = min(y for _, y in piece.cells)
        color = self._color_of(piece.name, piece.color)
        for x, y in piece.cells:
            rect = pygame.Rect(left + (x - min_x) * size, top + (y - min_y) * size, size, size)
            self._block(self.screen, rect, color, piece.image)
        return (max(y for _, y in piece.cells) - min_y + 1) * size

    def _block(self, surface: pygame.Surface, rect: pygame.Rect, color: AnyColor, image: str | None):
        if image:
            surface.blit(self._image(image, rect.size), rect)
            return
        style = self.theme.block_style
        draw = style if callable(style) else BLOCK_STYLES[style]
        draw(surface, rect, pygame.Color(color))

    def _cell_rect(self, board: pygame.Rect, x: int, y: int) -> pygame.Rect | None:
        if y < 0:
            return None  # above the board
        return pygame.Rect(board.left + x * self.cell, board.top + y * self.cell, self.cell, self.cell)

    def _color_of(self, name: str, color: Color) -> Color:
        """The color of a piece. The theme can change it."""
        return self.theme.piece_colors.get(name, color)

    def _add_bloom(self):
        """Glow: blur the blocks by shrinking and stretching them, then add that light on top."""
        size = self.screen.get_size()
        for blur in (6, 16):
            small = pygame.transform.smoothscale(self.glow, (size[0] // blur, size[1] // blur))
            self.screen.blit(pygame.transform.smoothscale(small, size), (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # ---------- small helpers ----------

    def _text(self, text: str, size: int, color: AnyColor, position: tuple[int, int], center: bool = False):
        """Write text. Big text gets a shadow so you can read it on top of blocks."""
        font = self.fonts[size]
        layers = [("black", 3), (color, 0)] if size >= 36 else [(color, 0)]
        for layer_color, offset in layers:
            image = font.render(text, True, layer_color)
            rect = image.get_rect(center=position) if center else image.get_rect(topleft=position)
            self.screen.blit(image, rect.move(offset, offset))

    def _shade(self, rect: pygame.Rect, color: AnyColor, alpha: int):
        layer = pygame.Surface(rect.size)
        layer.fill(color)
        layer.set_alpha(alpha)
        self.screen.blit(layer, rect)

    def _update_flicker(self, seconds: float):
        """With theme.flicker, the lights fail now and then for a moment."""
        self.flicker_left = max(0.0, self.flicker_left - seconds)
        if self.theme.flicker and not self.flicker_left and random.random() < 0.004:
            self.flicker_left = random.uniform(0.05, 0.25)

    def _font(self, size: int) -> pygame.font.Font:
        name = self.theme.font
        if name and os.path.exists(name):
            return pygame.font.Font(name, size)
        return pygame.font.SysFont(name or "dejavusansmono,menlo,consolas,monospace", size * 3 // 4, bold=True)

    def _image(self, path: str, size: tuple[int, int]) -> pygame.Surface:
        key = f"{path}@{size}"
        if key not in self.images:
            if not os.path.exists(path):
                raise FileNotFoundError(f"The image '{path}' doesn't exist.")
            self.images[key] = pygame.transform.smoothscale(pygame.image.load(path).convert_alpha(), size)
        return self.images[key]

    def _load_background(self) -> pygame.Surface | None:
        """The background image, a bit darker so the board stands out."""
        path = self.theme.background_image
        if not path:
            return None
        image = self._image(path, self.screen.get_size()).copy()
        darker = pygame.Surface(image.get_size())
        darker.set_alpha(160)
        image.blit(darker, (0, 0))
        return image


def _wrap(text: str, width: int) -> list[str]:
    """Split text into lines of at most width letters."""
    lines = []
    for paragraph in text.splitlines():
        line = ""
        for word in paragraph.split():
            if line and len(line) + 1 + len(word) > width:
                lines.append(line)
                line = word
            else:
                line = f"{line} {word}".strip()
        lines.append(line)
    return lines


def _check_theme(game: Tetris, style: str | Callable):
    """Clear messages for a block style or color that doesn't exist."""
    if not callable(style) and style not in BLOCK_STYLES:
        raise ValueError(f"There is no block style called '{style}'. Pick one of: {', '.join(BLOCK_STYLES)}.")
    theme = get_theme(game.theme)
    for piece in game.pieces:
        color = theme.piece_colors.get(piece.name, piece.color)
        try:
            pygame.Color(color)
        except ValueError:
            raise ValueError(f"Piece '{piece.name}' has color {color!r}, which is not a color. "
                             "Try a name like 'red', a code like '#ff0000' or (255, 0, 0).") from None


# ---------- block styles ----------
# Each one draws a single block. Make your own with the same three arguments and
# use it in a theme: Theme(block_style=my_block)

def _glow_block(surface: pygame.Surface, rect: pygame.Rect, color: pygame.Color):
    outer = rect.inflate(-2, -2)
    inner = outer.inflate(-rect.width // 3, -rect.height // 3)
    pygame.draw.rect(surface, color.lerp("white", 0.15), outer)
    pygame.draw.rect(surface, color.lerp("black", 0.25), inner)
    pygame.draw.line(surface, "white", outer.topleft, outer.topright)
    pygame.draw.line(surface, "white", outer.topleft, outer.bottomleft)


def _classic_block(surface: pygame.Surface, rect: pygame.Rect, color: pygame.Color):
    edge = max(2, rect.width // 8)
    pygame.draw.rect(surface, color, rect)
    light, dark = color.lerp("white", 0.45), color.lerp("black", 0.45)
    pygame.draw.rect(surface, light, (rect.left, rect.top, rect.width, edge))
    pygame.draw.rect(surface, light, (rect.left, rect.top, edge, rect.height))
    pygame.draw.rect(surface, dark, (rect.left, rect.bottom - edge, rect.width, edge))
    pygame.draw.rect(surface, dark, (rect.right - edge, rect.top, edge, rect.height))


def _flat_block(surface: pygame.Surface, rect: pygame.Rect, color: pygame.Color):
    pygame.draw.rect(surface, color, rect.inflate(-2, -2))


def _round_block(surface: pygame.Surface, rect: pygame.Rect, color: pygame.Color):
    pygame.draw.rect(surface, color, rect.inflate(-2, -2), border_radius=rect.width // 3)


def _outline_block(surface: pygame.Surface, rect: pygame.Rect, color: pygame.Color):
    pygame.draw.rect(surface, color.lerp("black", 0.7), rect.inflate(-2, -2))
    pygame.draw.rect(surface, color, rect.inflate(-4, -4), 2)


def _pixel_block(surface: pygame.Surface, rect: pygame.Rect, color: pygame.Color):
    pygame.draw.rect(surface, color.lerp("black", 0.5), rect)
    pygame.draw.rect(surface, color, rect.inflate(-4, -4))
    dot = max(2, rect.width // 6)
    pygame.draw.rect(surface, color.lerp("white", 0.6), (rect.left + 4, rect.top + 4, dot, dot))


BLOCK_STYLES = {
    "glow": _glow_block,
    "classic": _classic_block,
    "flat": _flat_block,
    "round": _round_block,
    "outline": _outline_block,
    "pixel": _pixel_block,
}
