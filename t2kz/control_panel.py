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

        # Define slider dimensions first
        self.slider_width = 200
        self.slider_height = 20

        # Calculate the total width of all elements
        total_elements_width = 4 * self.button_width + self.slider_width
        spacing = (self.width - total_elements_width) / 5

        # Position buttons and slider
        self.qwerty_button = pygame.Rect(spacing, self.y + (self.height - self.button_height) / 2, self.button_width, self.button_height)
        self.asdf_button = pygame.Rect(2 * spacing + self.button_width, self.y + (self.height - self.button_height) / 2, self.button_width, self.button_height)
        self.zxcv_button = pygame.Rect(3 * spacing + 2 * self.button_width, self.y + (self.height - self.button_height) / 2, self.button_width, self.button_height)
        self.pause_button = pygame.Rect(4 * spacing + 3 * self.button_width, self.y + (self.height - self.button_height) / 2, self.button_width, self.button_height)

        # Position speed control slider
        self.slider_x = 5 * spacing + 4 * self.button_width
        self.slider_y = self.y + (self.height - self.slider_height) / 2
        self.slider_rect = pygame.Rect(self.slider_x, self.slider_y, self.slider_width, self.slider_height)
        self.slider_handle_width = 10
        self.slider_handle_rect = pygame.Rect(self.slider_x, self.slider_y, self.slider_handle_width, self.slider_height)
        self.dragging_slider = False

        self.slider_handle_rect.x = self.slider_x + (self.slider_width - self.slider_handle_width) // 2  # Start at middle (speed 1)

    def handle_event(self, event):
        if self.game.waiting_to_start:  # Remove the 'or self.game.paused' condition
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.qwerty_button.collidepoint(event.pos):
                    self.game.toggle_keyboard_section('qwerty')
                elif self.asdf_button.collidepoint(event.pos):
                    self.game.toggle_keyboard_section('asdf')
                elif self.zxcv_button.collidepoint(event.pos):
                    self.game.toggle_keyboard_section('zxcv')
                elif self.slider_rect.collidepoint(event.pos):
                    self.dragging_slider = True
                    self.update_slider(event.pos[0])
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_slider = False
            elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
                self.update_slider(event.pos[0])
        if event.type == pygame.MOUSEBUTTONDOWN and self.pause_button.collidepoint(event.pos):
            self.game.toggle_pause()

    def update_slider(self, x):
        if self.game.waiting_to_start:  # Remove the 'or self.game.paused' condition
            new_x = max(self.slider_x, min(x - self.slider_handle_width // 2, self.slider_x + self.slider_width - self.slider_handle_width))
            self.slider_handle_rect.x = new_x
            speed_factor = 0.5 + (new_x - self.slider_x) / (self.slider_width - self.slider_handle_width)
            self.game.update_zombie_speed(speed_factor)

    def reset_speed_slider(self):
        self.slider_handle_rect.x = self.slider_x + (self.slider_width - self.slider_handle_width) // 2
        self.game.update_zombie_speed(1.0)

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), (0, self.y, self.width, self.height))
        
        self.draw_button(screen, self.qwerty_button, "QWERTY", self.game.qwerty_enabled)
        self.draw_button(screen, self.asdf_button, "ASDF", self.game.asdf_enabled)
        self.draw_button(screen, self.zxcv_button, "ZXCV", self.game.zxcv_enabled)
        self.draw_button(screen, self.pause_button, "PAUSE", self.game.paused)

        # Draw speed control slider
        pygame.draw.rect(screen, (150, 150, 150), self.slider_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.slider_handle_rect)
        
        font = pygame.font.Font(None, 24)
        speed_text = font.render(f"Speed: {self.game.current_speed_factor:.2f}", True, (0, 0, 0))
        speed_text_rect = speed_text.get_rect(center=(self.slider_x + self.slider_width // 2, self.slider_y - 15))
        screen.blit(speed_text, speed_text_rect)

        if not self.game.waiting_to_start:  # Change this condition
            disabled_overlay = pygame.Surface((self.slider_width, self.slider_height), pygame.SRCALPHA)
            disabled_overlay.fill((200, 200, 200, 128))  # Semi-transparent gray
            screen.blit(disabled_overlay, (self.slider_x, self.slider_y))

    def draw_button(self, screen, rect, text, enabled):
        color = (0, 255, 0) if enabled else (255, 0, 0)
        pygame.draw.rect(screen, color, rect)
        font = pygame.font.Font(None, 24)
        text_surf = font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)