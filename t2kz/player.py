import pygame
import sys
import math  # Add this import

class Player:
    def __init__(self, game):
        self.game = game
        self.x = game.width // 2
        self.y = (game.height - 100) // 2  # Center in the arena
        self.radius = 20
        self.proximity_circles = [100, 200, 300]  # Radii for proximity contours

    def update(self):
        pass

    def draw(self, screen):
        # Draw proximity contours
        for radius in self.proximity_circles:
            pygame.draw.circle(screen, (200, 200, 200), (self.x, self.y), radius, 1)

        # Draw player
        pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), self.radius)

    def collides_with(self, zombie):
        distance = ((self.x - zombie.x) ** 2 + (self.y - zombie.y) ** 2) ** 0.5
        return distance < (self.radius + zombie.radius)

    def distance_to(self, zombie):
        dx = self.x - zombie.x
        dy = self.y - zombie.y
        return math.sqrt(dx**2 + dy**2)