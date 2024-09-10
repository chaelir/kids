import pygame
import random
import string

class Zombie:
    def __init__(self, game):
        self.game = game
        self.x = random.randint(0, game.width)
        self.y = 0
        self.speed = random.uniform(0.5, 2)
        self.radius = 15
        self.letter = self.generate_letter()

    def generate_letter(self):
        if self.game.qwerty_enabled and self.game.asdf_enabled and self.game.zxcv_enabled:
            return random.choice(string.ascii_lowercase)
        
        available_letters = ""
        if self.game.qwerty_enabled:
            available_letters += "qwertyuiop"
        if self.game.asdf_enabled:
            available_letters += "asdfghjkl"
        if self.game.zxcv_enabled:
            available_letters += "zxcvbnm"
        
        return random.choice(available_letters) if available_letters else "?"

    def update(self):
        self.y += self.speed
        if self.y > self.game.height - 100:
            self.game.remove_zombie(self)
            self.game.score -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), self.radius)
        font = pygame.font.Font(None, 24)
        text = font.render(self.letter, True, (0, 0, 0))
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)