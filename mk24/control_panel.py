import pygame

class ControlPanel:
    def __init__(self, game):
        self.game = game
        self.basic_symbols = ['+', '-', '*', '/', '(', ')']
        self.advanced_symbols = ['!', '^']  # Keep ^ for display
        self.symbols = self.basic_symbols.copy()
        self.symbol_buttons = []
        
        # Define all buttons
        self.all_buttons = [
            ("Advanced", self.toggle_advanced_symbols),  # Changed from "Toggle" to "Advanced"
            ("Reveal", self.reveal_solution),
            ("Redraw", self.redraw_cards),
            ("Timer", self.toggle_game_mode),
            ("Submit", self.submit_formula),
            ("Clear", self.clear_formula)
        ]
        
        self.create_buttons()
        self.create_symbol_buttons()
        self.update_symbols(self.game.advanced_symbols_enabled)

    def create_buttons(self):
        button_width = 100
        button_height = 40
        total_width = self.game.width - 20  # 10px margin on each side
        button_spacing = (total_width - (len(self.all_buttons) * button_width)) // (len(self.all_buttons) - 1)
        
        y = 500  # Vertical position of buttons
        
        self.buttons = []
        for i, (text, _) in enumerate(self.all_buttons):
            x = 10 + i * (button_width + button_spacing)
            self.buttons.append((pygame.Rect(x, y, button_width, button_height), text))

    def create_symbol_buttons(self):
        self.symbol_buttons = []
        x, y = 50, 300
        for symbol in self.symbols:
            button = pygame.Rect(x, y, 50, 50)
            self.symbol_buttons.append((button, symbol))
            x += 60
            if x > 650:
                x = 50
                y += 60

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button, (text, action) in zip(self.buttons, self.all_buttons):
                if button[0].collidepoint(event.pos):
                    action()
                    break
            else:
                for button, symbol in self.symbol_buttons:
                    if button.collidepoint(event.pos):
                        self.game.solution_panel.add_to_formula(symbol)

    def toggle_advanced_symbols(self):
        self.game.advanced_symbols_enabled = not self.game.advanced_symbols_enabled
        self.update_symbols(self.game.advanced_symbols_enabled)
        print(f"Advanced symbols {'enabled' if self.game.advanced_symbols_enabled else 'disabled'}")

    def reveal_solution(self):
        solution = self.game.reveal_solution()
        self.game.solution_panel.display_solution(solution)

    def redraw_cards(self):
        self.game.redraw_cards()

    def toggle_game_mode(self):
        self.game.toggle_game_mode()

    def submit_formula(self):
        self.game.solution_panel.evaluate_formula()

    def clear_formula(self):
        self.game.solution_panel.clear_formula()

    def update_symbols(self, advanced_enabled):
        self.symbols = self.basic_symbols + (self.advanced_symbols if advanced_enabled else [])
        self.create_symbol_buttons()

    def draw(self, screen):
        # Draw symbol buttons
        for button, symbol in self.symbol_buttons:
            pygame.draw.rect(screen, (200, 200, 200), button)
            font = pygame.font.Font(None, 36)
            text = font.render(symbol, True, (0, 0, 0))
            text_rect = text.get_rect(center=button.center)
            screen.blit(text, text_rect)

        # Draw main buttons
        for button, text in self.buttons:
            if text == "Advanced":
                color = (0, 255, 0) if self.game.advanced_symbols_enabled else (255, 0, 0)
            elif text == "Timer":
                color = (0, 255, 0) if self.game.is_timed_mode else (255, 0, 0)
            else:
                color = (128, 0, 128)  # Purple for all other buttons
            
            pygame.draw.rect(screen, color, button)
            font = pygame.font.Font(None, 24)
            text_surface = font.render(text, True, (255, 255, 255))  # White text
            text_rect = text_surface.get_rect(center=button.center)
            screen.blit(text_surface, text_rect)

        # Draw advanced symbols status
        status_text = "Advanced: ON" if self.game.advanced_symbols_enabled else "Advanced: OFF"
        status_surface = font.render(status_text, True, (0, 0, 0))
        screen.blit(status_surface, (10, 550))

        # Draw game mode status
        if self.game.is_timed_mode:
            minutes, seconds = divmod(self.game.countdown, 60)
            mode_text = f"Timer: {minutes:02d}:{seconds:02d}"
        else:
            mode_text = "Timer: OFF"
        mode_surface = font.render(mode_text, True, (0, 0, 0))
        screen.blit(mode_surface, (200, 550))
