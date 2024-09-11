import pygame
import random
import math
import sys
import time

class Zombie:
    def __init__(self, game):
        self.game = game
        self.radius = 20  # Increased radius for better visibility
        self.spawn_position()
        self.speed = random.uniform(0.5, 1.0)  # Slower speed range
        self.letter = self.generate_letter()  # Store letter as generated (uppercase)
        self.is_dying = False
        self.bullet_pos = None
        self.bullet_speed = 3  # Reduced speed for better visibility
        self.creation_time = time.time()
        print(f"New zombie created with letter: {self.letter}", file=sys.stderr)

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
            available_letters += "QWERTYUIOP"
        if self.game.asdf_enabled:
            available_letters += "ASDFGHJKL"
        if self.game.zxcv_enabled:
            available_letters += "ZXCVBNM"
        
        if not available_letters:
            print("Warning: No keyboard rows enabled!")
            return "?"
        
        chosen_letter = random.choice(available_letters)
        print(f"Generated letter for zombie: {chosen_letter}")
        return chosen_letter

    def update(self):
        if self.is_dying:
            return self.update_bullet()
        else:
            dx = self.game.player.x - self.x
            dy = self.game.player.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance != 0:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
        return True

    def start_dying(self):
        self.is_dying = True
        self.bullet_pos = [self.game.player.x, self.game.player.y]
        print(f"Zombie {self.letter} started dying animation", file=sys.stderr)

    def update_bullet(self):
        if not self.is_dying or self.bullet_pos is None:
            return False

        dx = self.x - self.bullet_pos[0]
        dy = self.y - self.bullet_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > self.bullet_speed:
            self.bullet_pos[0] += (dx / distance) * self.bullet_speed
            self.bullet_pos[1] += (dy / distance) * self.bullet_speed
            return False
        else:
            print(f"Bullet hit Zombie {self.letter}", file=sys.stderr)
            return True

    def bullet_hit(self):
        return self.is_dying and self.update_bullet()

    def draw(self, screen, color):
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        font = pygame.font.Font(None, 36)  # Increased font size
        text = font.render(self.letter, True, (0, 0, 0))
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)

        if self.is_dying and self.bullet_pos:
            pygame.draw.circle(screen, (255, 0, 0), (int(self.bullet_pos[0]), int(self.bullet_pos[1])), 5)