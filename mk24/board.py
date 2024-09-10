import pygame
import random
from card import Card

class Board:
    def __init__(self, game):
        self.game = game
        self.cards = []
        self.generate_cards()

    def generate_cards(self):
        self.cards = [Card(random.randint(1, 10)) for _ in range(4)]

    def draw(self, screen):
        for i, card in enumerate(self.cards):
            card.draw(screen, 50 + i * 100, 50)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for card in self.cards:
                if card.is_clicked(event.pos):
                    self.game.solution_panel.add_to_formula(str(card.value))
                    self.cards.remove(card)
                    break

    def put_back_number(self, value):
        self.cards.append(Card(value))
