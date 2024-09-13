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
        self.position_cards()

    def position_cards(self):
        for i, card in enumerate(self.cards):
            card.rect.topleft = (50 + i * 100, 50)

    def draw(self, screen):
        for card in self.cards:
            card.draw(screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for card in self.cards[:]:  # Iterate over a copy of the list
                if card.rect.collidepoint(event.pos):
                    if self.game.solution_panel.add_to_formula(str(card.value)):
                        self.cards.remove(card)
                    break

    def put_back_number(self, value):
        new_card = Card(value)
        self.cards.append(new_card)
        self.position_cards()  # Reposition all cards to ensure proper layout
