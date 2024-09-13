import pygame
import math
import re

class SolutionPanel:
    def __init__(self, game):
        self.game = game
        self.formula = []
        self.used_numbers = set()  # Track used card numbers
        self.formula_rects = []
        self.solution_text = ""
        self.solution_color = (0, 0, 0)  # Default black color
        self.clear_solution_display()

    def add_to_formula(self, value):
        if value.isdigit():
            if value in self.used_numbers:
                return False  # Number already used
            self.used_numbers.add(value)
        self.formula.append(value)
        return True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.formula_rects):
                if rect.collidepoint(event.pos):
                    self.remove_from_formula(i)
                    break

    def remove_from_formula(self, index):
        value = self.formula.pop(index)
        if value.isdigit():
            self.used_numbers.remove(value)
            self.game.board.put_back_number(int(value))

    def reset_formula(self):
        self.formula = []
        self.used_numbers.clear()

    def clear_formula(self):
        for value in self.formula:
            if value.isdigit():
                self.game.board.put_back_number(int(value))
        self.reset_formula()

    def evaluate_formula(self):
        try:
            if len(self.used_numbers) != 4:
                raise ValueError("Not all cards are used")
            
            formula_str = ''.join(self.formula)
            result = self.calculate_result(formula_str)
            if result == 24:  # Check for exact equality
                self.game.start_flash((0, 255, 0))  # Green flash
                self.game.display_message("Success! Correct solution.")
                self.game.increment_solved_count()  # Increment the solved count
                self.game.redraw_cards()
                self.clear_solution_display()  # Clear solution display
            else:
                self.game.start_flash((255, 0, 0))  # Red flash
                self.game.display_message("Incorrect. Try again!")
        except Exception as e:
            print(f"Evaluation error: {e}")
            self.game.start_flash((255, 0, 0))  # Red flash
            self.game.display_message("Invalid formula. Try again!")

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

        # Draw solution text
        solution_surface = font.render(self.solution_text, True, self.solution_color)
        screen.blit(solution_surface, (50, 450))

    def display_solution(self, solution: str):
        self.solution_text = solution
        self.solution_color = (0, 255, 0)  # Green color for the solution

    def clear_solution_display(self):
        self.solution_text = ""
        self.solution_color = (0, 0, 0)  # Reset to default black color
