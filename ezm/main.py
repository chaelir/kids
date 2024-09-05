import pygame
import sys
from ezm.game import Game
from ezm.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def initialize_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("EscapeZombieMazia")
    return screen

def main_game_loop(game, clock):
    running = True
    while running:
        if game.state == "playing":
            running = game.update_gameplay()
        else:
            running = game.update_static_screen()
        clock.tick(FPS)
    return running

def cleanup():
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    screen = initialize_game()
    game = Game(screen)
    clock = pygame.time.Clock()
    
    running = main_game_loop(game, clock)
    
    cleanup()