import pygame
import random
from board import Board
from control_panel import ControlPanel
from solution_panel import SolutionPanel
from typing import List, Optional
import itertools
import math

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
        self.countdown = 120  # 2 minute countdown
        self.last_second = pygame.time.get_ticks()
        
        self.flash_start = 0
        self.flash_duration = 500  # 0.5 seconds
        self.flash_color = (255, 255, 255)  # Default white

        self.advanced_symbols_enabled = False

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
            self.screen.fill(self.flash_color)
        else:
            self.screen.fill((255, 255, 255))  # Normal white background
        
        self.board.draw(self.screen)
        self.control_panel.draw(self.screen)
        self.solution_panel.draw(self.screen)
        
        timer_text = self.font.render(f"Time: {self.countdown}", True, (0, 0, 0))
        self.screen.blit(timer_text, (10, 10))
        
        pygame.display.flip()

    def reset_game(self):
        self.countdown = 120
        self.last_second = pygame.time.get_ticks()
        self.board.generate_cards()
        self.solution_panel.reset_formula()

    def redraw_cards(self):
        self.board.generate_cards()
        self.solution_panel.reset_formula()

    def start_flash(self, color):
        self.flash_start = pygame.time.get_ticks()
        self.flash_color = color

    def is_flashing(self):
        return pygame.time.get_ticks() - self.flash_start < self.flash_duration

    def toggle_advanced_symbols(self):
        self.advanced_symbols_enabled = not self.advanced_symbols_enabled
        self.control_panel.update_symbols(self.advanced_symbols_enabled)

    def reveal_solution(self) -> str:
        cards = [card.value for card in self.board.cards]
        solution = self.find_solution(cards)
        if solution:
            return f"{solution} = 24"
        else:
            return "No solution exists"

    def find_solution(self, cards: List[int]) -> Optional[str]:
        operations = ['+', '-', '*', '/']
        if self.advanced_symbols_enabled:
            operations.extend(['^', '!'])

        for nums in itertools.permutations(cards):
            for ops in itertools.product(operations, repeat=3):
                formula = self.generate_formula(nums, ops)
                if self.evaluate_formula(formula) == 24:
                    return formula
        return None

    def generate_formula(self, nums: tuple, ops: tuple) -> str:
        formula = f"{nums[0]}{ops[0]}{nums[1]}{ops[1]}{nums[2]}{ops[2]}{nums[3]}"
        return formula

    def evaluate_formula(self, formula: str) -> Optional[float]:
        try:
            result = self.calculate_result(formula)
            return result if abs(result - 24) < 1e-6 else None
        except:
            return None

    def calculate_result(self, formula: str) -> float:
        def factorial(n):
            return math.factorial(int(n))

        def power(base, exp):
            return math.pow(base, exp)

        # Replace ^ with ** for power operation
        formula = formula.replace('^', '**')

        # Handle factorial
        while '!' in formula:
            formula = re.sub(r'(\d+)!', r'factorial(\1)', formula)

        # Evaluate the expression
        return eval(formula, {"factorial": factorial, "math": math})
