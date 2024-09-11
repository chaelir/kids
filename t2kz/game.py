import pygame
import random
import sys
from arena import Arena
from control_panel import ControlPanel
from player import Player
from zombie import Zombie
from timer import Timer
from score import Score

class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 700  # Increased height for control panel
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Type to Kill Zombies")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        pygame.key.set_repeat(200, 25)  # Enable key repeat
        self.ime_text = ""
        
        self.arena = Arena(self)
        self.control_panel = ControlPanel(self)
        self.player = Player(self)
        self.zombies = []
        self.timer = Timer(self, 120)  # 2 minutes
        self.score = Score(self)
        
        self.game_over = False
        
        self.qwerty_enabled = False
        self.asdf_enabled = True
        self.zxcv_enabled = False

        self.zombie_spawn_rate = 0.02  # 2% chance per frame
        self.max_zombies = 5  # Increased maximum number of zombies

        print("Game initialized", file=sys.stderr)

    def run(self):
        print("Game started", file=sys.stderr)
        while not self.game_over:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        self.show_game_over_screen()
        pygame.quit()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            elif event.type == pygame.KEYDOWN:
                print(f"Key pressed: {pygame.key.name(event.key)}", file=sys.stderr)
                self.handle_keydown(event)
            elif event.type == pygame.TEXTINPUT:
                print(f"Text input: {event.text}", file=sys.stderr)
                self.handle_text_input(event.text)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.control_panel.handle_event(event)

    def handle_text_input(self, text):
        self.ime_text += text
        print(f"Current IME text: {self.ime_text}", file=sys.stderr)
        if len(self.ime_text) == 1:
            self.attempt_kill_zombie(self.ime_text)
            self.ime_text = ""

    def handle_keydown(self, event):
        if event.key == pygame.K_RETURN:
            if self.ime_text:
                self.attempt_kill_zombie(self.ime_text)
                self.ime_text = ""
        elif event.key == pygame.K_BACKSPACE:
            self.ime_text = self.ime_text[:-1]
        elif event.unicode.isalpha():
            key_pressed = event.unicode.lower()
            self.attempt_kill_zombie(key_pressed)

    def attempt_kill_zombie(self, key):
        print(f"Attempting to kill zombie with key: {key}", file=sys.stderr)
        if self.kill_zombie(key):
            self.score.increase()

    def kill_zombie(self, key):
        print(f"  Kill Zombie: Checking for zombie with letter '{key}'", file=sys.stderr)
        key_lower = key.lower()
        matching_zombies = [
            zombie for zombie in self.zombies
            if zombie.letter.lower() == key_lower and not zombie.is_dying
        ]
        
        if matching_zombies:
            # Sort matching zombies by distance to player (closest first)
            closest_zombie = min(matching_zombies, key=lambda z: self.player.distance_to(z))
            closest_zombie.start_dying()
            print(f"    Zombie {closest_zombie.letter} started dying", file=sys.stderr)
            return True
        
        print(f"  Kill Zombie: No matching zombie found for letter '{key}'", file=sys.stderr)
        return False

    def update(self):
        self.timer.update()
        if self.timer.time_left <= 0:
            self.game_over = True

        self.player.update()
        zombies_to_remove = []
        for zombie in self.zombies:
            zombie.update()
            if zombie.is_dying:
                if zombie.bullet_hit():
                    zombies_to_remove.append(zombie)
            elif self.player.collides_with(zombie):
                self.game_over = True
                print("Game over: Player collided with a zombie!", file=sys.stderr)

        for zombie in zombies_to_remove:
            self.remove_zombie(zombie)
        
        self.spawn_zombie()

    def draw(self):
        self.screen.fill((255, 255, 255))  # White background
        self.arena.draw(self.screen)
        self.player.draw(self.screen)
        for zombie in self.zombies:
            color = self.get_zombie_color(zombie)
            zombie.draw(self.screen, color)
        self.control_panel.draw(self.screen)
        self.timer.draw(self.screen)
        self.score.draw(self.screen)

        # Draw IME text
        if self.ime_text:
            font = pygame.font.Font(None, 36)
            ime_surf = font.render(f"IME: {self.ime_text}", True, (0, 0, 0))
            self.screen.blit(ime_surf, (10, self.height - 50))

        pygame.display.flip()

    def spawn_zombie(self):
        if len(self.zombies) < self.max_zombies and random.random() < self.zombie_spawn_rate:
            new_zombie = Zombie(self)
            self.zombies.append(new_zombie)
            print(f"New zombie spawned with letter: {new_zombie.letter}", file=sys.stderr)  # Debug print

    def remove_zombie(self, zombie):
        if zombie in self.zombies:
            self.zombies.remove(zombie)
            print(f"Zombie {zombie.letter} removed from the game", file=sys.stderr)
        else:
            print(f"Warning: Zombie {zombie.letter} not found in the game's zombie list", file=sys.stderr)

    def toggle_keyboard_section(self, section):
        if section == 'qwerty':
            self.qwerty_enabled = not self.qwerty_enabled
        elif section == 'asdf':
            self.asdf_enabled = not self.asdf_enabled
        elif section == 'zxcv':
            self.zxcv_enabled = not self.zxcv_enabled
        print(f"Keyboard sections enabled: QWERTY={self.qwerty_enabled}, ASDF={self.asdf_enabled}, ZXCV={self.zxcv_enabled}", file=sys.stderr)  # Debug print

    def show_game_over_screen(self):
        self.screen.fill((0, 0, 0))
        game_over_text = self.font.render("Game Over", True, (255, 255, 255))
        score_text = self.font.render(f"Final Score: {self.score.value}", True, (255, 255, 255))
        self.screen.blit(game_over_text, (self.width // 2 - 100, self.height // 2 - 50))
        self.screen.blit(score_text, (self.width // 2 - 100, self.height // 2 + 50))
        pygame.display.flip()
        pygame.time.wait(3000)  # Wait for 3 seconds before quitting

    def get_zombie_color(self, zombie):
        if zombie.is_dying:
            return (255, 165, 0)  # Orange color for dying zombies
        return (0, 255, 0)  # Green color for active zombies