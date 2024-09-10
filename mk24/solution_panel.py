import pygame
import math
import re

class SolutionPanel:
    def __init__(self, game):
        self.game = game
        self.formula = []
        self.submit_button = pygame.Rect(600, 500, 100, 50)
        self.clear_button = pygame.Rect(450, 500, 100, 50)
        self.formula_rects = []
        self.solution_text = ""
        self.solution_color = (0, 0, 0)  # Default black color

    def add_to_formula(self, value):
        self.formula.append(value)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.submit_button.collidepoint(event.pos):
                self.evaluate_formula()
            elif self.clear_button.collidepoint(event.pos):
                self.clear_formula()
            else:
                for i, rect in enumerate(self.formula_rects):
                    if rect.collidepoint(event.pos):
                        self.remove_from_formula(i)
                        break

    def remove_from_formula(self, index):
        value = self.formula.pop(index)
        if value.isdigit():
            self.game.board.put_back_number(int(value))

    def reset_formula(self):
        self.formula = []

    def clear_formula(self):
        for value in self.formula:
            if value.isdigit():
                self.game.board.put_back_number(int(value))
        self.formula = []

    def evaluate_formula(self):
        try:
            result = self.calculate_result(''.join(self.formula))
            if abs(result - 24) < 1e-6:  # Use a small epsilon for float comparison
                print("Correct! The formula equals 24.")
                self.game.start_flash((0, 255, 0))  # Green flash
                self.game.redraw_cards()
            else:
                print(f"Incorrect. The formula equals {result}.")
                self.game.start_flash((255, 0, 0))  # Red flash
        except Exception as e:
            print(f"Invalid formula: {e}")
            self.game.start_flash((255, 0, 0))  # Red flash

    def calculate_result(self, formula):
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

    def draw(self, screen):
        font = pygame.font.Font(None, 36)
        x, y = 50, 500
        self.formula_rects = []

        for value in self.formula:
            text = font.render(value, True, (0, 0, 0))
            text_rect = text.get_rect(topleft=(x, y))
            screen.blit(text, text_rect)
            self.formula_rects.append(text_rect)
            x += text_rect.width + 5

        pygame.draw.rect(screen, (0, 255, 0), self.submit_button)
        submit_text = font.render("Submit", True, (0, 0, 0))
        submit_rect = submit_text.get_rect(center=self.submit_button.center)
        screen.blit(submit_text, submit_rect)

        pygame.draw.rect(screen, (255, 0, 0), self.clear_button)
        clear_text = font.render("Clear", True, (0, 0, 0))
        clear_rect = clear_text.get_rect(center=self.clear_button.center)
        screen.blit(clear_text, clear_rect)

        # Draw solution text in green
        solution_surface = font.render(self.solution_text, True, self.solution_color)
        screen.blit(solution_surface, (50, 450))

    def display_solution(self, solution: str):
        self.solution_text = solution
        self.solution_color = (0, 255, 0)  # Green color for the solution
