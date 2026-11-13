import time
import random
from pathlib import Path

import pygame
from pygame.math import Vector2
from textquest.effects import say

G = 800

WIDTH = 1200
HEIGHT = 800
BGCOLOR = pygame.Color(0, 0, 0)
BG_PATH = Path(__file__).parent / "media" / "arcade.webp"

COOLDOWN = 0.8
HITS_NEEDED = 13
TOTAL_SECONDS = 35

APPLE_PATH = Path(__file__).parent / "media" / "apple.png"
PIE_PATH = Path(__file__).parent / "media" / "pie.png"
MUSIC_PATH = Path(__file__).parent / "media" / "crunch.mp3"


RATE = 60
DT = 1.0 / float(RATE)

COLL_DIST = 60


class Body:
    def __init__(self, pos, vel: Vector2):
        self.pos = pos
        self.vel = vel
        self.acc = Vector2(0, 0)

    def set_acc(self, new_acc: Vector2):
        self.acc = new_acc

    def update(self, dt: float):
        self.vel += dt * self.acc
        self.pos += dt * self.vel


def shoot_the_pies():
    say("""Controls:
    - Aim your cursor at where you want to shoot the apple
    - Shoot by tapping [LEFT MOUSE BUTTON] or [SPACE]""")
    
    pygame.init()
    pygame.display.init()
    pygame.font.init()
    pygame.mixer.init()
    
    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.play(loops=-1)

    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Shoot the pies!")
    font = pygame.font.Font(None, 40)
    
    bg_img = pygame.image.load(BG_PATH).convert_alpha()
    
    apple_img = pygame.image.load(APPLE_PATH).convert_alpha()
    apple_obj = pygame.transform.scale(apple_img, (120, 120))

    pie_img = pygame.image.load(PIE_PATH).convert_alpha()
    pie_obj = pygame.transform.scale(pie_img, (120, 120))

    apples: list[Body] = []
    pies: list[Body] = []
    
    last_shoot = time.monotonic() + COOLDOWN
    pie_timer = random.uniform(0, 1)
    
    hits = 0

    clock = pygame.time.Clock()
    end_time = time.monotonic() + TOTAL_SECONDS
    while time.monotonic() < end_time:
        # update logic
        can_shoot = time.monotonic() - last_shoot >= COOLDOWN
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        shoot_x, shoot_y = WIDTH // 2, HEIGHT - 50
                    
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                say("Nobody escapes the throwing of pies! Mwuahahahahaha")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if can_shoot:
                    v = 1000 * (Vector2(mouse_x, mouse_y) - Vector2(shoot_x, shoot_y)).normalize()
                    apples.append(Body(Vector2(shoot_x, shoot_y), v))
                    apples[-1].acc = Vector2(0, G)
                    
                    last_shoot = time.monotonic()
                                
        if pie_timer <= 0:
            side = random.choice(["left", "right"])
            
            p = Vector2()
            v = Vector2()
            if side == "left":
                p = Vector2(-100, 200)
                v = Vector2(900, 0).rotate(random.uniform(-15, -30))
            elif side == "right":
                p = Vector2(WIDTH + 100, 200)
                v = Vector2(-900, 0).rotate(random.uniform(15, 30))
                
            pies.append(Body(p, v))
            pies[-1].acc = Vector2(0, G)
            
            pie_timer = random.uniform(2, 4)
        pie_timer -= DT
        
        for apple in apples:
            if apple.pos.y < 0:
                apples.remove(apple)
        
            apple.update(DT)
                    
        for pie in pies:
            if pie.pos.y < 0:
                pies.remove(pie)
            
            pie.update(DT)
            
        for apple in apples:
            for pie in pies:
                if apple.pos.distance_to(pie.pos) <= COLL_DIST:
                    hits += 1
                    pie_timer = random.uniform(0.2, 0.5) # when hitting, the new pie gets added sooner
                    pies.remove(pie)
        
        # begin draw
        window.fill(BGCOLOR)
        
        window.blit(pygame.transform.scale(bg_img, (WIDTH, HEIGHT)))

        if can_shoot:
            window.blit(apple_obj, Vector2(shoot_x, shoot_y) - Vector2(40, 40))


        for apple in apples:
            window.blit(apple_obj, apple.pos - Vector2(40, 40))
            
        for pie in pies:
            window.blit(pie_obj, pie.pos - Vector2(40, 40))

        time_left = int(end_time - time.monotonic()) + 1
        window.blit(font.render(f"Hits: {hits} / {HITS_NEEDED}   Time: {time_left}", True, "white"), (10, 10))

        # end draw
        pygame.display.flip()
        clock.tick(RATE)

    pygame.mixer.music.stop()
    pygame.display.quit()
    return hits >= HITS_NEEDED


def make_game():
    return shoot_the_pies()


if __name__ == "__main__":
    make_game()
