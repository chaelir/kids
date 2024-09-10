import pygame

class Arena:
    def __init__(self, game):
        self.game = game
        self.width = game.width
        self.height = game.height - 100  # Leave space for control panel

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), (0, 0, self.width, self.height))