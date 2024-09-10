import pygame
import random
from board import Board
from control_panel import ControlPanel
from solution_panel import SolutionPanel

class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("24 Game")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.board = Board(self)
        self.control_panel = ControlPanel(self)
        self.solution_panel = SolutionPanel(self)
        
        self.running = True
        self.countdown = 60  # 1 minute countdown
        self.last_second = pygame.time.get_ticks()
        
        self.flash_start = 0
        self.flash_duration = 500  # 0.5 seconds

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.USEREVENT:
                self.redraw_cards()  # Automatically redraw cards after the flash
            else:
                self.board.handle_event(event)
                self.control_panel.handle_event(event)
                self.solution_panel.handle_event(event)

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_second >= 1000:
            self.countdown -= 1
            self.last_second = current_time
            if self.countdown <= 0:
                self.running = False

    def draw(self):
        if self.is_flashing():
            self.screen.fill((0, 255, 0))  # Flash green
        else:
            self.screen.fill((255, 255, 255))  # Normal white background
        
        self.board.draw(self.screen)
        self.control_panel.draw(self.screen)
        self.solution_panel.draw(self.screen)
        
        timer_text = self.font.render(f"Time: {self.countdown}", True, (0, 0, 0))
        self.screen.blit(timer_text, (10, 10))
        
        pygame.display.flip()

    def reset_game(self):
        self.countdown = 60
        self.last_second = pygame.time.get_ticks()
        self.board.generate_cards()
        self.solution_panel.reset_formula()

    def redraw_cards(self):
        self.board.generate_cards()
        self.solution_panel.reset_formula()

    def start_flash(self):
        self.flash_start = pygame.time.get_ticks()

    def is_flashing(self):
        return pygame.time.get_ticks() - self.flash_start < self.flash_duration
