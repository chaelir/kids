import pygame

class Score:
    def __init__(self, game):
        self.game = game
        self.value = 0

    def increase(self):
        self.value += 1

    def draw(self, screen):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.value}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))