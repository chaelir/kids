import pygame

class HP:
    def __init__(self, initial_value=10):
        self.initial_value = initial_value
        self.value = initial_value
        self.font = pygame.font.Font(None, 36)

    def decrease(self, amount=1):
        self.value = max(0, self.value - amount)

    def reset(self):
        self.value = self.initial_value

    def draw(self, screen, x, y):
        hp_text = f"HP: {self.value}"
        text_surface = self.font.render(hp_text, True, (255, 0, 0))  # Red color for HP
        screen.blit(text_surface, (x, y))