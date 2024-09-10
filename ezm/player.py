import pygame
import unittest
from ezm.constants import ORANGE, YELLOW, PLAYER_SPEED, PLAYER_SIZE

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=pos)
        self.has_sword = False
        self.speed = PLAYER_SPEED

    def collect_sword(self):
        self.has_sword = True
        self.image.fill(YELLOW)

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def update(self):
        try:
            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
            dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
            self.move(dx, dy)
        except pygame.error:
            # If Pygame is not initialized, do nothing
            pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def reset(self, pos):
        self.rect.center = pos
        self.has_sword = False
        self.image.fill(ORANGE)

class TestPlayer(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.player = Player((100, 100))

    def test_init(self):
        self.assertEqual(self.player.rect.center, (100, 100))
        self.assertFalse(self.player.has_sword)
        self.assertEqual(self.player.speed, PLAYER_SPEED)

    def test_collect_sword(self):
        self.player.collect_sword()
        self.assertTrue(self.player.has_sword)
        self.assertEqual(self.player.image.get_at((0, 0)), YELLOW)

    def test_move(self):
        initial_pos = self.player.rect.center
        self.player.move(1, 1)
        self.assertEqual(self.player.rect.center, (initial_pos[0] + PLAYER_SPEED, initial_pos[1] + PLAYER_SPEED))

    def test_reset(self):
        self.player.collect_sword()
        self.player.reset((200, 200))
        self.assertEqual(self.player.rect.center, (200, 200))
        self.assertFalse(self.player.has_sword)
        self.assertEqual(self.player.image.get_at((0, 0)), ORANGE)

if __name__ == '__main__':
    unittest.main()