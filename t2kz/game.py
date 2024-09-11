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

        self.zombie_spawn_rate = 0.01  # Increased spawn rate (1% chance per frame)
        self.max_zombies = 2  # Maximum number of zombies allowed on screen

    def run(self):
        while not self.game_over:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            # The following line has been removed:
            # print(f"Current number of zombies: {len(self.zombies)}", file=sys.stderr)
        self.show_game_over_screen()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            elif event.type == pygame.KEYDOWN:
                print(f"Key pressed: {pygame.key.name(event.key)}", file=sys.stderr)  # Debug print
                if event.unicode.isalpha():
                    key_pressed = event.unicode.lower()
                    print(f"Alphabetic key pressed: {key_pressed}", file=sys.stderr)  # Debug print
                    print(f"Current zombies: {[z.letter.lower() for z in self.zombies]}", file=sys.stderr)
                    killed_zombie = self.player.handle_input(key_pressed)
                    if killed_zombie:
                        self.score.increase()
                        print(f"Zombie killed with letter: {key_pressed}", file=sys.stderr)  # Debug print
                    else:
                        print(f"No zombie killed with letter: {key_pressed}", file=sys.stderr)  # Debug print
                    print(f"Remaining zombies: {[z.letter.lower() for z in self.zombies]}", file=sys.stderr)  # Debug print
            self.control_panel.handle_event(event)

    def update(self):
        self.timer.update()
        if self.timer.time_left <= 0:
            self.game_over = True

        self.player.update()
        for zombie in self.zombies[:]:  # Use a copy of the list to safely remove zombies
            zombie.update()
            if zombie.is_dying:
                continue  # Skip collision check for dying zombies
            if self.player.collides_with(zombie):
                self.game_over = True
                print("Game over: Player collided with a zombie!", file=sys.stderr)  # Debug print
        
        self.spawn_zombie()

    def draw(self):
        self.screen.fill((255, 255, 255))  # White background
        self.arena.draw(self.screen)
        self.player.draw(self.screen)
        for zombie in self.zombies:
            zombie.draw(self.screen)
        self.control_panel.draw(self.screen)
        self.timer.draw(self.screen)
        self.score.draw(self.screen)

        pygame.display.flip()

    def spawn_zombie(self):
        if len(self.zombies) < self.max_zombies and random.random() < self.zombie_spawn_rate:
            new_zombie = Zombie(self)
            self.zombies.append(new_zombie)
            print(f"New zombie spawned with letter: {new_zombie.letter}", file=sys.stderr)  # Debug print

    def remove_zombie(self, zombie):
        if zombie in self.zombies:
            self.zombies.remove(zombie)
            print(f"Zombie {zombie.letter} removed from the game", file=sys.stderr)  # Debug print
        else:
            print(f"Zombie {zombie.letter} not found in the game's zombie list", file=sys.stderr)  # Debug print

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