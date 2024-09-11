import pygame

class Score:
    def __init__(self, game):
        self.game = game
        self.value = 0

    def increase(self, points=1):
        self.value += points