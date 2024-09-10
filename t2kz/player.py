import pygame

class Player:
    def __init__(self, game):
        self.game = game
        self.x = game.width // 2
        self.y = game.height - 150
        self.radius = 20

    def handle_input(self, key):
        for zombie in self.game.zombies:
            if zombie.letter.lower() == key.lower():
                self.game.remove_zombie(zombie)
                break

    def update(self):
        pass

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), self.radius)