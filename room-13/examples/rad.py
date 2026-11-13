import pygame
from pathlib import Path
import math
import random
from textquest.effects import jumpscare
import sys

MUSIC = Path(__file__).parent / "media" / "radmusic.mp3"
JUMPSCARE = Path(__file__).parent / "media" / "scream.mp3"
IMAGE = Path(__file__).parent / "media" / "hello-kitty.png"
WIDTH = 640
HEIGHT = 480

win = False


def make_game():
    def show_popup(message):
        font = pygame.font.SysFont(None, 40)
        text = font.render(message, True, (255, 255, 255))
        subtext = pygame.font.SysFont(None, 24).render("Press any key or click to continue", True, (180, 180, 180))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 15))
        sub_rect = subtext.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25))
        box_rect = text_rect.union(sub_rect).inflate(40, 30)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.draw.rect(display, (255, 255, 255), box_rect, 2)
            pygame.draw.rect(display, (25, 25, 25), box_rect)
            display.blit(text, text_rect)
            display.blit(subtext, sub_rect)
            pygame.display.flip()
    display = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Wheel of Kitty")
    pygame.init()
    pygame.mixer.init()

    pygame.mixer.music.load(MUSIC)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    # values of rotation
    surf = pygame.Surface((400, 400))
    surf.fill((0, 0, 0, 0))
    surf.set_colorkey((255, 0, 0))
    center = (surf.get_width() // 2, surf.get_height() // 2)
    clock = pygame.time.Clock()
    fps = random.uniform(10, 30)
    friction = 0.97
    stopped = False

    pygame.draw.circle(surf, (255, 255, 255), center, 150)
    for i in range(8):
        angle = math.radians(i * 45)
        x = center[0] + int(150 * math.cos(angle))
        y = center[1] + int(150 * math.sin(angle))
        pygame.draw.line(surf, (0, 0, 0), center, (x, y), 3)
    zoom = 0.9
    img_size = int(400 * zoom)
    img = pygame.image.load(IMAGE)
    img = pygame.transform.scale(img, (img_size, img_size))
    img_center = img.get_rect(center=center)
    surf.blit(img, img_center, special_flags=pygame.BLEND_RGBA_MULT)
    blitted_circle = display.blit(surf, (0, 0))
    blitted_circle.center = (WIDTH // 2, HEIGHT // 2)

    # game loop
    degree = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        display.fill((0, 0, 0))

        rotated_surf = pygame.transform.rotate(surf, degree)
        rotation_circle = rotated_surf.get_rect()
        rotation_circle.center = blitted_circle.center
        display.blit(rotated_surf, rotation_circle)

        # pointer of wheel
        wheel_x = WIDTH // 2
        top_y = (HEIGHT // 2) - 145

        pointer_points = [
            (wheel_x - 10, top_y - 15),
            (wheel_x + 10, top_y - 15),
            (wheel_x, top_y + 10)
        ]

        pygame.draw.polygon(display, (255, 255, 255), pointer_points)
        pygame.draw.polygon(display, (0, 0, 0), pointer_points, 3)

        clock.tick(fps)
        pygame.display.flip()

        if not stopped:
            degree += fps
            fps *= friction

            if fps < 3:
                running = False
                stopped = True
                degree = int(round(degree / 45) * 45)
                vak = int(round(degree / 45)) % 8
                if vak == 2:
                    show_popup("You Win!")
                    return True
                jumpscare(sound=JUMPSCARE)
                pygame.time.delay(1000)

    pygame.mixer.music.stop()
    pygame.quit()
    return False


if __name__ == "__main__":
    make_game()
