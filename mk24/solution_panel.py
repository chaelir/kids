import pygame
import math
import re

class SolutionPanel:
    def __init__(self, game):
        self.game = game
        self.formula = []
        self.submit_button = pygame.Rect(50, 500, 100, 50)
        self.clear_button = pygame.Rect(200, 500, 100, 50)
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
            formula_str = ''.join(self.formula)
            result = self.calculate_result(formula_str)
            if result == 24:  # Check for exact equality
                self.game.start_flash((0, 255, 0))  # Green flash
                self.game.increment_solved_count()  # Increment the solved count
                self.game.redraw_cards()
            else:
                self.game.start_flash((255, 0, 0))  # Red flash
        except Exception:
            self.game.start_flash((255, 0, 0))  # Red flash

    def calculate_result(self, formula):
        def factorial(n):
            return math.factorial(int(n))

        def power(base, exp):
            return math.pow(float(base), float(exp))

        # Handle factorial
        while '!' in formula:
            formula = re.sub(r'(\d+)!', r'factorial(\1)', formula)

        # Handle power operation
        while '^' in formula:
            formula = re.sub(r'(\d+|\))\^(\d+|\()', r'power(\1,\2)', formula)

        # Evaluate the expression
        result = eval(formula, {"factorial": factorial, "power": power, "math": math})
        
        # Round the result to handle floating point imprecision
        return round(result, 10)

    def draw(self, screen):
        font = pygame.font.Font(None, 36)
        x, y = 50, 400
        self.formula_rects = []

        for value in self.formula:
            # Convert ** back to ^ for display
            display_value = '^' if value == '**' else value
            text = font.render(display_value, True, (0, 0, 0))
            text_rect = text.get_rect(topleft=(x, y))
            screen.blit(text, text_rect)
            self.formula_rects.append(text_rect)
            x += text_rect.width + 5

        # Draw buttons
        buttons = [
            (self.submit_button, "Submit", (0, 255, 0)),
            (self.clear_button, "Clear", (255, 0, 0))
        ]
        
        for button, text, color in buttons:
            pygame.draw.rect(screen, color, button)
            text_surface = font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=button.center)
            screen.blit(text_surface, text_rect)

        # Draw solution text in green
        solution_surface = font.render(self.solution_text, True, self.solution_color)
        screen.blit(solution_surface, (50, 450))

    def display_solution(self, solution: str):
        self.solution_text = solution
        self.solution_color = (0, 255, 0)  # Green color for the solution
