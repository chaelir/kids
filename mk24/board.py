import pygame
import random
from card import Card

class Board:
    def __init__(self, game):
        self.game = game
        self.cards = []
        self.generate_cards()
        self.redraw_button = pygame.Rect(650, 100, 100, 50)

    def generate_cards(self):
        self.cards = []
        numbers = random.sample(range(1, 11), 4)
        x, y = 50, 100
        for number in numbers:
            self.cards.append(Card(number, x, y))
            x += 120

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.redraw_button.collidepoint(event.pos):
                self.game.redraw_cards()
            else:
                for card in self.cards:
                    if card.rect.collidepoint(event.pos) and not card.used:
                        self.game.solution_panel.add_to_formula(str(card.number))
                        card.used = True

    def put_back_number(self, number):
        for card in self.cards:
            if card.number == number and card.used:
                card.used = False
                break

    def draw(self, screen):
        for card in self.cards:
            card.draw(screen)
        
        pygame.draw.rect(screen, (200, 200, 200), self.redraw_button)
        font = pygame.font.Font(None, 24)
        text = font.render("Redraw", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.redraw_button.center)
        screen.blit(text, text_rect)
