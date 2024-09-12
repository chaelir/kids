import pygame
import random
import sys
import math
import locale
from arena import Arena
from control_panel import ControlPanel
from player import Player
from zombie import Zombie
from timer import Timer
from score import Score
from hp import HP  # Add this import at the top of the file
import json
import os

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
        self.timer = Timer(self, 30)  # Set timer to 30 seconds
        self.score = Score(self)
        self.hp = HP(10)  # Add this line after self.score initialization
        
        self.game_over = False
        self.paused = False
        self.waiting_to_start = True
        self.start_message_font = pygame.font.Font(None, 48)
        
        self.qwerty_enabled = True  # Changed to True
        self.asdf_enabled = True
        self.zxcv_enabled = True  # Changed to True

        self.zombie_spawn_rate = 0.02  # 2% chance per frame
        self.max_zombies = 5  # Increased maximum number of zombies

        self.base_zombie_speed = 0.25  # Reduced to 50% of the current speed
        self.max_zombie_speed = 1.0  # Reduced to 100% of the current speed
        self.current_speed_factor = 1.0  # Changed to 1.0 (default speed)
        self.game_complete = False
        self.game_success = False  # New attribute to track game success

        print("Game initialized, waiting for start", file=sys.stderr)

        self.high_scores = self.load_high_scores()

        self.reset_to_start()

    def reset_to_start(self):
        self.waiting_to_start = True
        self.game_over = False
        self.game_complete = False
        self.game_success = False
        self.paused = False
        self.zombies = []
        self.score.reset()
        self.hp.reset()
        self.timer.reset()
        self.current_speed_factor = 1.0  # Reset speed to default
        self.control_panel.reset_speed_slider()  # Add this line
        print("Game reset to start state", file=sys.stderr)

    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r') as f:
                scores = json.load(f)
                return sorted(scores, reverse=True)[:5]  # Ensure we have at most 5 scores, sorted
        except (FileNotFoundError, json.JSONDecodeError):
            return [0] * 5  # Initialize with five zero scores if file doesn't exist or is invalid

    def save_high_scores(self):
        with open('high_scores.json', 'w') as f:
            json.dump(self.high_scores, f)

    def update_high_scores(self, score):
        self.high_scores.append(score)
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:5]  # Keep only top 5
        self.save_high_scores()

    def run(self):
        print("Game started", file=sys.stderr)
        while True:  # Changed from 'while not self.game_over'
            self.handle_events()
            self.draw()
            if not self.waiting_to_start and not self.paused and not self.game_over and not self.game_complete:
                self.update()
            self.clock.tick(60)
        pygame.quit()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                print(f"Key pressed: {pygame.key.name(event.key)}", file=sys.stderr)
                if (self.game_over or self.game_complete) and event.key == pygame.K_RETURN:
                    self.reset_to_start()
                elif self.paused and event.key == pygame.K_RETURN:
                    self.reset_to_start()
                elif self.waiting_to_start and event.key == pygame.K_RETURN:
                    self.start_game()
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    self.toggle_pause()
                elif not self.paused and not self.waiting_to_start and not self.game_over and not self.game_complete:
                    self.handle_keydown(event)
            elif event.type == pygame.TEXTINPUT and not self.paused and not self.waiting_to_start and not self.game_over and not self.game_complete:
                print(f"Text input: {event.text}", file=sys.stderr)
                self.handle_text_input(event.text)
            
            # Always process control panel events
            self.control_panel.handle_event(event)

    def start_game(self):
        self.waiting_to_start = False
        self.timer.start()
        print("Game started", file=sys.stderr)

    def toggle_pause(self):
        self.paused = not self.paused
        print(f"Game {'paused' if self.paused else 'resumed'}", file=sys.stderr)
        if self.paused:
            self.timer.pause()
        else:
            self.timer.resume()

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
            if zombie.letter == key_lower and not zombie.is_dying
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
            self.game_success = True  # Player survived the timer
            self.game_over = True
            return

        self.player.update()
        zombies_to_remove = []
        for zombie in self.zombies:
            zombie.update()
            if zombie.is_dying:
                if zombie.bullet_hit():
                    zombies_to_remove.append(zombie)
            elif self.player.collides_with(zombie):
                self.hp.decrease()  # Decrease HP when a zombie reaches the player
                zombies_to_remove.append(zombie)  # Remove the zombie after it deals damage
                if self.hp.value <= 0:
                    self.game_over = True
                    print("Game over: Player HP reached 0!", file=sys.stderr)

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
        self.hp.draw(self.screen, 10, 50)  # Draw HP below the timer

        if self.waiting_to_start:
            self.draw_start_message()
        elif self.paused:
            self.draw_pause_overlay()
        elif self.game_over or self.game_complete:
            self.draw_game_over_screen()

        pygame.display.flip()

    def draw_start_message(self):
        start_text = self.start_message_font.render("Press ENTER to start", True, (0, 0, 0))
        text_rect = start_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(start_text, text_rect)

    def draw_pause_overlay(self):
        pause_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(pause_overlay, (0, 0))
        
        pause_text = self.start_message_font.render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2 - 60))
        self.screen.blit(pause_text, pause_rect)

        resume_text = self.font.render("Press SPACE to resume", True, (255, 255, 255))
        resume_rect = resume_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(resume_text, resume_rect)

        return_text = self.font.render("Press ENTER to return to start", True, (255, 255, 255))
        return_rect = return_text.get_rect(center=(self.width // 2, self.height // 2 + 40))
        self.screen.blit(return_text, return_rect)

    def spawn_zombie(self):
        if len(self.zombies) < self.max_zombies and random.random() < self.zombie_spawn_rate:
            new_zombie = Zombie(self)
            spawn_x, spawn_y = self.generate_spawn_position()
            new_zombie.x, new_zombie.y = spawn_x, spawn_y
            new_speed = self.base_zombie_speed + self.current_speed_factor * (self.max_zombie_speed - self.base_zombie_speed)
            new_zombie.update_speed(new_speed)
            self.zombies.append(new_zombie)
            print(f"New zombie spawned with letter: {new_zombie.letter} at position ({spawn_x}, {spawn_y})", file=sys.stderr)

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

    def draw_game_over_screen(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        if self.game_success:
            main_text = self.font.render("Success!", True, (255, 255, 255))
        else:
            main_text = self.font.render("Game Over", True, (255, 255, 255))

        final_score = self.calculate_final_score()
        self.update_high_scores(final_score)
        
        score_text = self.font.render(f"Final Score: {final_score}", True, (255, 255, 255))
        speed_text = self.font.render(f"Speed Factor: {self.current_speed_factor:.2f}", True, (255, 255, 255))
        correct_types_text = self.font.render(f"Correct Types: {self.score.value}", True, (255, 255, 255))
        hp_text = self.font.render(f"Remaining HP: {self.hp.value}", True, (255, 255, 255))
        modes_text = self.font.render(f"Enabled Modes: {self.count_enabled_modes()}", True, (255, 255, 255))
        restart_text = self.font.render("Press ENTER to return to start", True, (255, 255, 255))

        y_offset = self.height // 2 - 200
        for text in [main_text, score_text, speed_text, correct_types_text, hp_text, modes_text]:
            text_rect = text.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 40

        # Display high scores
        high_score_text = self.font.render("Top 5 High Scores:", True, (255, 255, 255))
        self.screen.blit(high_score_text, (self.width // 2 - 100, y_offset))
        y_offset += 40

        for i, score in enumerate(self.high_scores, 1):
            score_text = self.font.render(f"{i}. {score}", True, (255, 255, 255))
            self.screen.blit(score_text, (self.width // 2 - 50, y_offset))
            y_offset += 30

        restart_rect = restart_text.get_rect(center=(self.width // 2, y_offset + 20))
        self.screen.blit(restart_text, restart_rect)

    def calculate_final_score(self):
        if not self.game_success and self.hp.value <= 0:
            return 0
        base_score = int(self.current_speed_factor * (self.score.value + self.hp.value))
        return base_score * self.count_enabled_modes()

    def count_enabled_modes(self):
        return sum([self.qwerty_enabled, self.asdf_enabled, self.zxcv_enabled])

    def get_zombie_color(self, zombie):
        if zombie.is_dying:
            return (255, 165, 0)  # Orange color for dying zombies
        return (0, 255, 0)  # Green color for active zombies

    def generate_spawn_position(self):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(self.player.proximity_circles[-1], 
                                  math.sqrt(self.width**2 + (self.height - 100)**2) / 2)
        spawn_x = self.player.x + distance * math.cos(angle)
        spawn_y = self.player.y + distance * math.sin(angle)
        
        # Ensure the zombie spawns within the visible area
        spawn_x = max(0, min(spawn_x, self.width))
        spawn_y = max(0, min(spawn_y, self.height - 100))
        
        return spawn_x, spawn_y

    def update_zombie_speed(self, speed_factor):
        if self.waiting_to_start:
            self.current_speed_factor = speed_factor
            new_speed = self.base_zombie_speed + speed_factor * (self.max_zombie_speed - self.base_zombie_speed)
            for zombie in self.zombies:
                zombie.update_speed(new_speed)
            print(f"Updated zombie speed factor to {speed_factor:.2f}", file=sys.stderr)