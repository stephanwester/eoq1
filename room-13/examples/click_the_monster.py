"""A minigame in a window: click the monster as many times as you can in 10 seconds.

A minigame is just a function. This one opens a pygame window, and when the time
is up it closes the window and returns the name of the next scene.

Run it with:  poetry run python examples/click_the_monster.py
"""
import random
import time
from pathlib import Path

import pygame

from textquest.game import Game
from textquest.scene import Option, Scene

SECONDS = 1
HITS_NEEDED = 0
WIDTH = 640
HEIGHT = 480

MONSTER = Path(__file__).parent / "media" / "monster.png"


def click_the_monster(game):
    pygame.display.init()
    pygame.font.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Click the monster!")
    font = pygame.font.Font(None, 40)
    monster = pygame.image.load(MONSTER).convert_alpha()
    spot = monster.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    clock = pygame.time.Clock()

    hits = 0
    end_time = time.monotonic() + SECONDS
    while time.monotonic() < end_time:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and spot.collidepoint(event.pos):
                hits += 1
                spot.x = random.randint(0, WIDTH - spot.width)  # it jumps away
                spot.y = random.randint(40, HEIGHT - spot.height)

        time_left = int(end_time - time.monotonic()) + 1
        window.fill("black")
        window.blit(monster, spot)
        window.blit(font.render(f"Hits: {hits}   Time: {time_left}", True, "white"), (10, 10))
        pygame.display.flip()
        clock.tick(60)

    pygame.display.quit()
    game.set("hits", hits)
    if hits >= HITS_NEEDED:
        return "survived"
    return "caught"


def make_game():
    game = Game("Click the Monster", start="machine 1")
    game.add(
        Scene("machine 1", title="The machine 1",
              text=f"A [blood]monster[/] blocks the way out! Hit it {HITS_NEEDED} times.",
              options=[Option("Fight back", action=click_the_monster)]),
        Scene("survived", title="Gone", ending="win",
              text=lambda game: f"{game.get('hits')} hits! It screams and runs away."),
        Scene("caught", title="Too Slow", ending="lose",
              text=lambda game: f"Only {game.get('hits')} hits. It's still smiling."),
    )
    return game


if __name__ == "__main__":
    make_game().run()
