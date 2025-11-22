# utils/audio_player.py
import pygame
import os

# تهيئة المحرك الصوتي بصمت
try:
    pygame.mixer.init()
except:
    pass

class AudioController:
    def __init__(self):
        self.current_file = None
        self.is_paused = False
        self.duration = 0

    def load(self, path):
        self.current_file = path
        try:
            pygame.mixer.music.load(path)
            self.is_paused = False
        except Exception as e:
            print(f"Audio Load Error: {e}")

    def play(self):
        if self.current_file:
            if self.is_paused:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.play()
            self.is_paused = False

    def pause(self):
        pygame.mixer.music.pause()
        self.is_paused = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_paused = False

    def get_pos(self):
        if pygame.mixer.music.get_busy() or self.is_paused:
            # pygame returns milliseconds, convert to seconds
            return pygame.mixer.music.get_pos() / 1000.0
        return 0

controller = AudioController()