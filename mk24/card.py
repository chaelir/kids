import pygame

class Card:
    def __init__(self, value):
        self.value = value
        self.rect = pygame.Rect(0, 0, 80, 120)  # Adjust size as needed
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        pygame.draw.rect(screen, (255, 255, 255), self.rect)  # White background
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)  # Black border
        text = self.font.render(str(self.value), True, (0, 0, 0))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)