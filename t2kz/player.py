import pygame
import sys

class Player:
    def __init__(self, game):
        self.game = game
        self.x = game.width // 2
        self.y = (game.height - 100) // 2  # Center in the arena
        self.radius = 20

    def update(self):
        pass

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), self.radius)

    def collides_with(self, zombie):
        distance = ((self.x - zombie.x) ** 2 + (self.y - zombie.y) ** 2) ** 0.5
        return distance < (self.radius + zombie.radius)