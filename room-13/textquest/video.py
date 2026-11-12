"""Short videos. A video plays in its own window, with sound, like the Tetris game.

ffmpeg reads the video file. imageio-ffmpeg comes with its own copy, so there's nothing to install.
"""
import os
import subprocess
import tempfile
import time

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import imageio_ffmpeg
import pygame

from textquest.errors import TextQuestError
from textquest.sound import start_mixer


def play_video(path, fullscreen=True):
    """Play a video file (like .mp4) and wait until it's done. Any key skips it."""
    if not os.path.exists(path):
        raise TextQuestError(f"Can't play video '{path}': there is no such file.")

    frames = imageio_ffmpeg.read_frames(path)
    info = next(frames)
    size = info["size"]

    pygame.display.init()
    flags = pygame.SCALED | pygame.FULLSCREEN if fullscreen else 0
    window = pygame.display.set_mode(size, flags)
    pygame.mouse.set_visible(False)
    try:
        with tempfile.TemporaryDirectory() as folder:
            _start_sound(path, os.path.join(folder, "sound.wav"))
            _show_frames(frames, window, size, info["fps"])
    finally:
        frames.close()
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()  # lets go of the temporary sound file
        pygame.display.quit()


def _show_frames(frames, window, size, fps):
    start = time.monotonic()
    for number, frame in enumerate(frames):
        for event in pygame.event.get():
            if event.type in {pygame.KEYDOWN, pygame.QUIT}:
                return
        late = time.monotonic() - start - number / fps
        if late > 1 / fps:
            continue  # the computer can't keep up: skip this frame to stay in time with the sound
        if late < 0:
            time.sleep(-late)
        window.blit(pygame.image.frombuffer(frame, size, "RGB"), (0, 0))
        pygame.display.flip()


def _start_sound(path, sound_file):
    """Copy the sound out of the video and play it. No sound in the video, or no speakers: no problem."""
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    copied = subprocess.run([ffmpeg, "-y", "-loglevel", "quiet", "-i", path, "-vn", sound_file], check=False)
    if copied.returncode == 0 and start_mixer():
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
