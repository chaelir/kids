import pygame
import random
from arena import Arena
from control_panel import ControlPanel
from player import Player
from zombie import Zombie

class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Type to Kill Zombies")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.arena = Arena(self)
        self.control_panel = ControlPanel(self)
        self.player = Player(self)
        self.zombies = []
        
        self.score = 0
        self.timer = 120  # 2 minutes
        self.game_over = False
        
        self.qwerty_enabled = True
        self.asdf_enabled = True
        self.zxcv_enabled = True

    def run(self):
        while not self.game_over:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            elif event.type == pygame.KEYDOWN:
                self.player.handle_input(event.unicode)
            self.control_panel.handle_event(event)

    def update(self):
        self.timer -= 1/60  # Decrease timer by 1/60th of a second
        if self.timer <= 0:
            self.game_over = True

        self.player.update()
        for zombie in self.zombies:
            zombie.update()
        
        self.spawn_zombie()

    def draw(self):
        self.screen.fill((255, 255, 255))  # White background
        self.arena.draw(self.screen)
        self.player.draw(self.screen)
        for zombie in self.zombies:
            zombie.draw(self.screen)
        self.control_panel.draw(self.screen)

        # Draw score and timer
        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        timer_text = self.font.render(f"Time: {int(self.timer)}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(timer_text, (self.width - 100, 10))

        pygame.display.flip()

    def spawn_zombie(self):
        if random.random() < 0.02:  # 2% chance to spawn a zombie each frame
            self.zombies.append(Zombie(self))

    def remove_zombie(self, zombie):
        self.zombies.remove(zombie)
        self.score += 1

    def toggle_keyboard_section(self, section):
        if section == 'qwerty':
            self.qwerty_enabled = not self.qwerty_enabled
        elif section == 'asdf':
            self.asdf_enabled = not self.asdf_enabled
        elif section == 'zxcv':
            self.zxcv_enabled = not self.zxcv_enabled