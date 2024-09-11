import pygame
import sys

class Player:
    def __init__(self, game):
        self.game = game
        self.x = game.width // 2
        self.y = (game.height - 100) // 2  # Center in the arena
        self.radius = 20

    def handle_input(self, key):
        print(f"Player handling input: {key}", file=sys.stderr)
        print(f"Current zombies before input: {[z.letter for z in self.game.zombies]}", file=sys.stderr)
        for zombie in self.game.zombies[:]:  # Create a copy of the list to iterate over
            print(f"Checking zombie with letter: {zombie.letter}", file=sys.stderr)
            if zombie.letter.lower() == key.lower() and not zombie.is_dying:
                zombie.start_dying()
                print(f"Zombie {key} started dying animation", file=sys.stderr)
                print(f"Zombies after starting death: {[z.letter for z in self.game.zombies]}", file=sys.stderr)
                return True  # Return True if a zombie was killed
        print(f"No matching zombie found for letter: {key}", file=sys.stderr)
        return False  # Return False if no zombie was killed

    def update(self):
        pass

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), self.radius)

    def collides_with(self, zombie):
        distance = ((self.x - zombie.x) ** 2 + (self.y - zombie.y) ** 2) ** 0.5
        return distance < (self.radius + zombie.radius)