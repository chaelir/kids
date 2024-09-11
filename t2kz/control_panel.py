import pygame

class ControlPanel:
    def __init__(self, game):
        self.game = game
        self.height = 100
        self.width = game.width
        self.y = game.height - self.height

        self.button_width = 100
        self.button_height = 40
        self.button_margin = 10

        self.qwerty_button = pygame.Rect(self.button_margin, self.y + self.button_margin, self.button_width, self.button_height)
        self.asdf_button = pygame.Rect(self.button_margin * 2 + self.button_width, self.y + self.button_margin, self.button_width, self.button_height)
        self.zxcv_button = pygame.Rect(self.button_margin * 3 + self.button_width * 2, self.y + self.button_margin, self.button_width, self.button_height)
        
        # Add pause button
        self.pause_button = pygame.Rect(self.width - self.button_width - self.button_margin, self.y + self.button_margin, self.button_width, self.button_height)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.qwerty_button.collidepoint(event.pos):
                self.game.toggle_keyboard_section('qwerty')
            elif self.asdf_button.collidepoint(event.pos):
                self.game.toggle_keyboard_section('asdf')
            elif self.zxcv_button.collidepoint(event.pos):
                self.game.toggle_keyboard_section('zxcv')
            elif self.pause_button.collidepoint(event.pos):
                self.game.toggle_pause()

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), (0, self.y, self.width, self.height))
        
        self.draw_button(screen, self.qwerty_button, "QWERTY", self.game.qwerty_enabled)
        self.draw_button(screen, self.asdf_button, "ASDF", self.game.asdf_enabled)
        self.draw_button(screen, self.zxcv_button, "ZXCV", self.game.zxcv_enabled)
        
        # Draw pause button
        self.draw_button(screen, self.pause_button, "PAUSE", self.game.paused)

    def draw_button(self, screen, rect, text, enabled):
        color = (0, 255, 0) if enabled else (255, 0, 0)
        pygame.draw.rect(screen, color, rect)
        font = pygame.font.Font(None, 24)
        text_surf = font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)