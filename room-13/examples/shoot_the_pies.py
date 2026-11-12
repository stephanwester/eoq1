import time
import random
from pathlib import Path

import pygame
from pygame.math import Vector2

from textquest.effects import say, jumpscare


G = 1000

WIDTH = 800
HEIGHT = 800
BGCOLOR = pygame.Color(0, 0, 0)

HITS_NEEDED = 12
SECONDS = 15

PIE = Path(__file__).parent / "media" / "pie.png"
APPLE = Path(__file__).parent / "media" / "apple.png"
JUMPSCARE = Path(__file__).parent / "media" / "scream.mp3"

RATE = 60
DT = 1.0 / float(RATE)

COLL_DIST = 80


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
    # TODO: explain controls
    
    pygame.display.init()
    pygame.font.init()

    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Shoot the pies!")
    font = pygame.font.Font(None, 40)

    apple_img = pygame.image.load(APPLE).convert_alpha()
    apple_obj = pygame.transform.scale(apple_img, (80, 80))
    
    pie_img = pygame.image.load(PIE).convert_alpha()
    pie_obj = pygame.transform.scale(pie_img, (80, 80))

    apples: list[Body] = []
    pies: list[Body] = []
    
    pie_timer = random.uniform(0, 1)
    
    hits = 0

    clock = pygame.time.Clock()
    end_time = time.monotonic() + SECONDS
    while time.monotonic() < end_time:
        # update logic
        mouse_x, mouse_y = pygame.mouse.get_pos()
        shoot_x, shoot_y = WIDTH // 2, HEIGHT - 50
                    
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                jumpscare(sound=JUMPSCARE)
                say("Nobody escapes the throwing of pies! Mwuahahahahaha")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                v = 2000 * (Vector2(mouse_x, mouse_y) - Vector2(shoot_x, shoot_y)).normalize()
                apples.append(Body(Vector2(shoot_x, shoot_y), v))
                apples[-1].acc = Vector2(0, G)
                                
        if pie_timer <= 0:
            v = Vector2(1000, 0).rotate(-30)
            pies.append(Body(Vector2(-100, 200), v))
            pies[-1].acc = Vector2(0, G)
            
            pie_timer = random.uniform(2, 4)
        pie_timer -= DT
        
        for apple in apples:
            if apple.pos.x < 0 or apple.pos.x > WIDTH or apple.pos.y < 0 or apple.pos.y > HEIGHT:
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

        for apple in apples:
            window.blit(apple_obj, apple.pos - (40, 40))
            
        for pie in pies:
            window.blit(pie_obj, pie.pos - (40, 40))

        time_left = int(end_time - time.monotonic()) + 1
        window.blit(font.render(f"Hits: {hits} / {HITS_NEEDED}   Time: {time_left}", True, "white"), (10, 10))

        # end draw
        pygame.display.flip()
        clock.tick(RATE)

    pygame.display.quit()
    if hits >= HITS_NEEDED:
        return True
    return False


def make_game():
    return shoot_the_pies()
    


if __name__ == "__main__":
    make_game()
