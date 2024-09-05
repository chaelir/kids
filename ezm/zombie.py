import pygame
import os
import unittest
from ezm.constants import ZOMBIE_SPEED, ZOMBIE_SIZE, CELL_SIZE

class Zombie(pygame.sprite.Sprite):
    def __init__(self, grid_pos):
        super().__init__()
        self.grid_position = grid_pos
        self.target_grid_position = self.grid_position
        self.move_progress = 0
        self.move_duration = 1
        
        # Load the zombie image from the assets folder
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets')
        self.image = pygame.image.load(os.path.join(asset_dir, "zombie.jpg")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (ZOMBIE_SIZE, ZOMBIE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = self.grid_to_pixel(self.grid_position)

    def update(self, dt):
        if self.grid_position != self.target_grid_position:
            self.move_progress += dt / self.move_duration
            if self.move_progress >= 1:
                self.grid_position = self.target_grid_position
                self.move_progress = 0
            current_pos = self.get_current_position()
            self.rect.center = self.grid_to_pixel(current_pos)

    def move_to(self, new_grid_pos):
        self.target_grid_position = new_grid_pos
        self.move_progress = 0

    def get_current_position(self):
        if self.grid_position == self.target_grid_position:
            return self.grid_position
        else:
            progress = min(self.move_progress, 1)
            row = self.grid_position[0] + (self.target_grid_position[0] - self.grid_position[0]) * progress
            col = self.grid_position[1] + (self.target_grid_position[1] - self.grid_position[1]) * progress
            return (row, col)

    def grid_to_pixel(self, grid_pos):
        return (grid_pos[1] * CELL_SIZE + CELL_SIZE // 2, grid_pos[0] * CELL_SIZE + CELL_SIZE // 2)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class TestZombie(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.zombie = Zombie((0, 0))

    def test_init(self):
        self.assertEqual(self.zombie.grid_position, (0, 0))
        self.assertEqual(self.zombie.target_grid_position, (0, 0))
        self.assertEqual(self.zombie.move_progress, 0)
        self.assertEqual(self.zombie.move_duration, 1)

    def test_move_to(self):
        self.zombie.move_to((1, 1))
        self.assertEqual(self.zombie.target_grid_position, (1, 1))
        self.assertEqual(self.zombie.move_progress, 0)

    def test_get_current_position(self):
        self.zombie.move_to((1, 1))
        self.zombie.move_progress = 0.5
        current_pos = self.zombie.get_current_position()
        self.assertAlmostEqual(current_pos[0], 0.5)
        self.assertAlmostEqual(current_pos[1], 0.5)

    def test_grid_to_pixel(self):
        pixel_pos = self.zombie.grid_to_pixel((1, 1))
        self.assertEqual(pixel_pos, (100, 100))

    def test_update(self):
        self.zombie.move_to((1, 1))
        self.zombie.update(0.5)
        self.assertEqual(self.zombie.move_progress, 0.5)
        self.zombie.update(0.5)
        self.assertEqual(self.zombie.grid_position, (1, 1))
        self.assertEqual(self.zombie.move_progress, 0)

if __name__ == '__main__':
    unittest.main()