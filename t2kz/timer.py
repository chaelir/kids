import pygame
import time

class Timer:
    def __init__(self, game, duration):
        self.game = game
        self.duration = duration
        self.start_time = None
        self.paused_time = 0
        self.is_paused = False
        self.time_left = duration

    def start(self):
        self.start_time = time.time()

    def update(self):
        if self.start_time is None:
            return
        if not self.is_paused:
            self.time_left = max(0, self.duration - (time.time() - self.start_time - self.paused_time))

    def draw(self, screen):
        minutes = int(self.time_left // 60)
        seconds = int(self.time_left % 60)
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        font = pygame.font.Font(None, 36)
        text_surface = font.render(timer_text, True, (0, 0, 0))
        screen.blit(text_surface, (10, 10))

    def pause(self):
        if not self.is_paused:
            self.is_paused = True
            self.pause_start_time = time.time()

    def resume(self):
        if self.is_paused:
            self.is_paused = False
            self.paused_time += time.time() - self.pause_start_time