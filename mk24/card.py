import pygame

class Card:
    def __init__(self, number, x, y):
        self.number = number
        self.rect = pygame.Rect(x, y, 100, 150)
        self.used = False

    def draw(self, screen):
        color = (200, 200, 200) if self.used else (255, 255, 255)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        font = pygame.font.Font(None, 72)
        text = font.render(str(self.number), True, (0, 0, 0))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)