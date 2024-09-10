import pygame

class ControlPanel:
    def __init__(self, game):
        self.game = game
        self.symbols = ['+', '-', '*', '/', '(', ')']
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        x, y = 50, 300
        for symbol in self.symbols:
            button = pygame.Rect(x, y, 50, 50)
            self.buttons.append((button, symbol))
            x += 60
            if x > 700:
                x = 50
                y += 60

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button, symbol in self.buttons:
                if button.collidepoint(event.pos):
                    self.game.solution_panel.add_to_formula(symbol)

    def draw(self, screen):
        for button, symbol in self.buttons:
            pygame.draw.rect(screen, (200, 200, 200), button)
            font = pygame.font.Font(None, 36)
            text = font.render(symbol, True, (0, 0, 0))
            text_rect = text.get_rect(center=button.center)
            screen.blit(text, text_rect)
