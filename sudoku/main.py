import pygame
import sys
from game_manager import GameManager
from sudoku_solver import SudokuSolver
from ui_manager import UIManager

pygame.init()

# Set up display
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")

# Initialize game components
solver = SudokuSolver()
game_manager = GameManager(solver)
ui_manager = UIManager(screen, game_manager)

# Start a new game
game_manager.new_game()

# Main game loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        ui_manager.handle_event(event)
    
    ui_manager.draw()
    pygame.display.flip()
    clock.tick(60)