import pygame

class ControlPanel:
    def __init__(self, game):
        self.game = game
        self.height = 100
        self.width = game.width
        self.y = game.height - self.height

        button_width = 120
        button_height = 40
        button_margin = 10

        self.qwerty_button = pygame.Rect(button_margin, self.y + button_margin, button_width, button_height)
        self.asdf_button = pygame.Rect(2 * button_margin + button_width, self.y + button_margin, button_width, button_height)
        self.zxcv_button = pygame.Rect(3 * button_margin + 2 * button_width, self.y + button_margin, button_width, button_height)
        self.restart_button = pygame.Rect(4 * button_margin + 3 * button_width, self.y + button_margin, button_width, button_height)
        self.quit_button = pygame.Rect(5 * button_margin + 4 * button_width, self.y + button_margin, button_width, button_height)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.qwerty_button.collidepoint(mouse_pos):
                self.game.toggle_keyboard_section('qwerty')
            elif self.asdf_button.collidepoint(mouse_pos):
                self.game.toggle_keyboard_section('asdf')
            elif self.zxcv_button.collidepoint(mouse_pos):
                self.game.toggle_keyboard_section('zxcv')
            elif self.restart_button.collidepoint(mouse_pos):
                self.game.__init__()  # Restart the game
            elif self.quit_button.collidepoint(mouse_pos):
                self.game.game_over = True

    def draw(self, screen):
        pygame.draw.rect(screen, (150, 150, 150), (0, self.y, self.width, self.height))
        
        self.draw_button(screen, self.qwerty_button, "QWERTY", self.game.qwerty_enabled)
        self.draw_button(screen, self.asdf_button, "ASDF", self.game.asdf_enabled)
        self.draw_button(screen, self.zxcv_button, "ZXCV", self.game.zxcv_enabled)
        self.draw_button(screen, self.restart_button, "Restart", True)
        self.draw_button(screen, self.quit_button, "Quit", True)

    def draw_button(self, screen, rect, text, enabled):
        color = (0, 255, 0) if enabled else (255, 0, 0)
        pygame.draw.rect(screen, color, rect)
        font = pygame.font.Font(None, 28)
        text_surf = font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)