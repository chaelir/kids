import pygame

class Timer:
    def __init__(self, game, duration):
        self.game = game
        self.duration = duration
        self.time_left = duration

    def update(self):
        self.time_left -= 1/60  # Decrease timer by 1/60th of a second

    def draw(self, screen):
        font = pygame.font.Font(None, 36)
        timer_text = font.render(f"Time: {int(self.time_left)}", True, (0, 0, 0))
        screen.blit(timer_text, (self.game.width - 120, 10))