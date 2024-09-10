import pygame
import random
from board import Board
from control_panel import ControlPanel
from solution_panel import SolutionPanel
from typing import List, Optional, Tuple
import itertools
import math
import re

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
        self.solved_count = 0  # Initialize the solved count

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
        
        # Add solved count display
        solved_text = self.font.render(f"Solved: {self.solved_count}", True, (0, 0, 0))
        self.screen.blit(solved_text, (self.width - 150, 10))
        
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
        def dfs(numbers: List[int], used: List[bool], expr: str, target: int = 24) -> Optional[Tuple[float, str]]:
            if sum(used) == len(numbers):
                try:
                    result = self.calculate_result(expr)
                    if abs(result - target) < 1e-6:
                        return (result, expr)
                except Exception:
                    # Silently ignore all exceptions
                    pass
                return None

            for i, num in enumerate(numbers):
                if used[i]:
                    continue

                new_used = used.copy()
                new_used[i] = True

                # Try using the number as is
                new_expr = f"{expr}{num}" if expr else str(num)
                solution = dfs(numbers, new_used, new_expr, target)
                if solution:
                    return solution

                # Try operations only if there's already a number in the expression
                if expr:
                    operations = ['+', '-', '*', '/']
                    if self.advanced_symbols_enabled:
                        operations.extend(['^'])

                    for op in operations:
                        # Avoid division by zero
                        if op == '/' and num == 0:
                            continue
                        new_expr = f"({expr}{op}{num})"
                        solution = dfs(numbers, new_used, new_expr, target)
                        if solution:
                            return solution

                    # Handle factorial separately
                    if self.advanced_symbols_enabled and num == int(num) and num >= 0:
                        new_expr = f"({expr}*{num}!)"
                        solution = dfs(numbers, new_used, new_expr, target)
                        if solution:
                            return solution

            return None

        solution = dfs(cards, [False] * len(cards), "")
        return solution[1] if solution else None

    def generate_formula(self, nums: tuple, ops: tuple) -> str:
        formula = str(nums[0])
        for i, op in enumerate(ops):
            if op == '!':
                formula += '!'
            else:
                if i + 1 < len(nums):
                    formula += f"{op}{nums[i+1]}"
        return formula

    def evaluate_formula(self, formula: str) -> Optional[float]:
        try:
            result = self.solution_panel.calculate_result(formula)
            return result if abs(result - 24) < 1e-6 else None
        except Exception as e:
            print(f"Error evaluating formula '{formula}': {e}")
            return None

    def calculate_result(self, formula: str) -> float:
        def factorial(n):
            if n < 0:
                raise ValueError("Factorial is not defined for negative numbers")
            return math.factorial(int(n))

        def power(base, exp):
            return math.pow(float(base), float(exp))

        # Replace ^ with ** for power operation
        formula = formula.replace('^', '**')

        # Handle factorial
        while '!' in formula:
            formula = re.sub(r'(\d+)!', r'factorial(\1)', formula)

        # Evaluate the expression
        try:
            return eval(formula, {"factorial": factorial, "power": power, "math": math})
        except Exception as e:
            #print(f"Error calculating result for '{formula}': {e}")
            raise

    def increment_solved_count(self):
        self.solved_count += 1
