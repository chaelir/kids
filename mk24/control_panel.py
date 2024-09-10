import pygame

class ControlPanel:
    def __init__(self, game):
        self.game = game
        self.basic_symbols = ['+', '-', '*', '/', '(', ')']
        self.advanced_symbols = ['!', '^']
        self.symbols = self.basic_symbols.copy()
        self.buttons = []
        self.toggle_button = pygame.Rect(700, 300, 80, 50)
        self.create_buttons()

    def create_buttons(self):
        self.buttons = []
        x, y = 50, 300
        for symbol in self.symbols:
            button = pygame.Rect(x, y, 50, 50)
            self.buttons.append((button, symbol))
            x += 60
            if x > 650:
                x = 50
                y += 60

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.toggle_button.collidepoint(event.pos):
                self.game.toggle_advanced_symbols()
            else:
                for button, symbol in self.buttons:
                    if button.collidepoint(event.pos):
                        self.game.solution_panel.add_to_formula(symbol)

    def update_symbols(self, advanced_enabled):
        self.symbols = self.basic_symbols + (self.advanced_symbols if advanced_enabled else [])
        self.create_buttons()

    def draw(self, screen):
        for button, symbol in self.buttons:
            pygame.draw.rect(screen, (200, 200, 200), button)
            font = pygame.font.Font(None, 36)
            text = font.render(symbol, True, (0, 0, 0))
            text_rect = text.get_rect(center=button.center)
            screen.blit(text, text_rect)

        # Draw toggle button
        pygame.draw.rect(screen, (150, 150, 150), self.toggle_button)
        font = pygame.font.Font(None, 24)
        text = font.render("Toggle", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.toggle_button.center)
        screen.blit(text, text_rect)

        # Draw advanced symbols status
        status_text = "Advanced: ON" if self.game.advanced_symbols_enabled else "Advanced: OFF"
        status_surface = font.render(status_text, True, (0, 0, 0))
        screen.blit(status_surface, (700, 360))
