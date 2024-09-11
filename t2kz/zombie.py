import pygame
import random
import math

class Zombie:
    def __init__(self, game):
        self.game = game
        self.radius = 20  # Increased radius for better visibility
        self.spawn_position()
        self.speed = random.uniform(0.1, 0.3)  # Further reduced speed range
        self.letter = self.generate_letter()
        self.is_dying = False
        self.bullet_pos = None
        self.bullet_speed = 5
        print(f"New zombie created with letter: {self.letter}")

    def spawn_position(self):
        side = random.choice(['top', 'right', 'bottom', 'left'])
        if side == 'top':
            self.x = random.randint(0, self.game.width)
            self.y = -self.radius
        elif side == 'right':
            self.x = self.game.width + self.radius
            self.y = random.randint(0, self.game.height - 100)
        elif side == 'bottom':
            self.x = random.randint(0, self.game.width)
            self.y = self.game.height - 100 + self.radius
        else:  # left
            self.x = -self.radius
            self.y = random.randint(0, self.game.height - 100)

    def generate_letter(self):
        available_letters = ""
        if self.game.qwerty_enabled:
            available_letters += "qwertyuiop"
        if self.game.asdf_enabled:
            available_letters += "asdfghjkl"
        if self.game.zxcv_enabled:
            available_letters += "zxcvbnm"
        
        if not available_letters:
            print("Warning: No keyboard rows enabled!")
            return "?"
        
        chosen_letter = random.choice(available_letters)
        print(f"Generated letter for zombie: {chosen_letter}")
        return chosen_letter

    def update(self):
        if self.is_dying:
            self.update_bullet()
        else:
            dx = self.game.player.x - self.x
            dy = self.game.player.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance != 0:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed

    def start_dying(self):
        self.is_dying = True
        self.bullet_pos = [self.game.player.x, self.game.player.y]

    def update_bullet(self):
        dx = self.x - self.bullet_pos[0]
        dy = self.y - self.bullet_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > self.bullet_speed:
            self.bullet_pos[0] += (dx / distance) * self.bullet_speed
            self.bullet_pos[1] += (dy / distance) * self.bullet_speed
        else:
            self.is_dying = False
            self.game.remove_zombie(self)

    def draw(self, screen):
        if self.is_dying:
            pygame.draw.circle(screen, (255, 0, 0), (int(self.bullet_pos[0]), int(self.bullet_pos[1])), 5)
        
        pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), self.radius)
        font = pygame.font.Font(None, 36)  # Increased font size
        text = font.render(self.letter, True, (0, 0, 0))
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)