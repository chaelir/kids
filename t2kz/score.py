import pygame

class Score:
    def __init__(self, game):
        self.game = game
        self.value = 0

    def increase(self, points=1):
        self.value += points

    def reset(self):
        self.value = 0

    def draw(self, screen):
        score_text = f"Score: {self.value}"
        font = pygame.font.Font(None, 36)
        text_surface = font.render(score_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.topright = (self.game.width - 10, 10)  # Position in the top-right corner
        screen.blit(text_surface, text_rect)