import pygame
from constants import RED, WHITE, SQUARE_SIZE, GREY, CROWN_COLOR

class Piece:
    PADDING = 15
    OUTLINE = 2
    CROWN_RADIUS = 10

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, win, x=None, y=None):
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, GREY, (x, y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (x, y), radius)
        if self.king:
            pygame.draw.circle(win, CROWN_COLOR, (x, y), self.CROWN_RADIUS)

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()