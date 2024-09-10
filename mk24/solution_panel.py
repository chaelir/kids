import pygame

class SolutionPanel:
    def __init__(self, game):
        self.game = game
        self.formula = []
        self.submit_button = pygame.Rect(600, 500, 100, 50)
        self.clear_button = pygame.Rect(450, 500, 100, 50)  # New clear button
        self.formula_rects = []

    def add_to_formula(self, value):
        self.formula.append(value)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.submit_button.collidepoint(event.pos):
                self.evaluate_formula()
            elif self.clear_button.collidepoint(event.pos):  # Handle clear button click
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

    def clear_formula(self):  # New method to clear the formula
        for value in self.formula:
            if value.isdigit():
                self.game.board.put_back_number(int(value))
        self.formula = []

    def evaluate_formula(self):
        try:
            result = eval(''.join(self.formula))
            if result == 24:
                print("Correct! The formula equals 24.")
                self.game.start_flash()
                self.game.redraw_cards()  # Redraw cards immediately
            else:
                print(f"Incorrect. The formula equals {result}.")
        except:
            print("Invalid formula.")

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

        # Draw the clear button
        pygame.draw.rect(screen, (255, 0, 0), self.clear_button)
        clear_text = font.render("Clear", True, (0, 0, 0))
        clear_rect = clear_text.get_rect(center=self.clear_button.center)
        screen.blit(clear_text, clear_rect)
