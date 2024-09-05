import unittest
from unittest.mock import patch, MagicMock
import pygame
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ezm.main import initialize_game, main_game_loop, cleanup
from ezm.constants import FPS, PLAYER_SIZE, CELL_SIZE
from ezm.player import Player
from ezm.maze import Maze
from ezm.zombie import Zombie
from ezm.game import Game

class TestMain(unittest.TestCase):

    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    def test_initialize_game(self, mock_set_caption, mock_set_mode):
        screen = initialize_game()
        mock_set_mode.assert_called_once()
        mock_set_caption.assert_called_once_with("EscapeZombieMazia")
        self.assertIsNotNone(screen)

    @patch('ezm.game.Game')
    @patch('pygame.time.Clock')
    def test_main_game_loop(self, mock_clock, mock_game):
        mock_game_instance = mock_game.return_value
        mock_game_instance.state = "playing"
        mock_game_instance.update_gameplay.return_value = False
        
        clock = mock_clock.return_value
        
        running = main_game_loop(mock_game_instance, clock)
        
        self.assertFalse(running)
        mock_game_instance.update_gameplay.assert_called_once()
        clock.tick.assert_called_once_with(FPS)

    @patch('pygame.quit')
    @patch('sys.exit')
    def test_cleanup(self, mock_exit, mock_quit):
        cleanup()
        mock_quit.assert_called_once()
        mock_exit.assert_called_once()

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player((0, 0))

    def test_player_initialization(self):
        self.assertEqual(self.player.rect.center, (0, 0))
        self.assertEqual(self.player.rect.size, (PLAYER_SIZE, PLAYER_SIZE))
        self.assertFalse(self.player.has_sword)

    def test_player_move(self):
        initial_pos = self.player.rect.center
        self.player.move(1, 0)
        self.assertEqual(self.player.rect.center, (initial_pos[0] + PLAYER_SPEED, initial_pos[1]))

    def test_player_collect_sword(self):
        self.player.collect_sword()
        self.assertTrue(self.player.has_sword)

class TestMaze(unittest.TestCase):
    def setUp(self):
        self.maze = Maze(9, 9)  # This will create a 9x9 maze

    def test_maze_initialization(self):
        self.assertEqual(len(self.maze.grid), 9)
        self.assertEqual(len(self.maze.grid[0]), 9)

    def test_maze_is_wall(self):
        self.maze.grid[0][0] = 1
        self.assertTrue(self.maze.is_wall(0, 0))
        self.maze.grid[0][0] = 0
        self.assertFalse(self.maze.is_wall(0, 0))

    def test_maze_get_valid_neighbors(self):
        self.maze.grid = [[0, 1, 0], [0, 0, 0], [0, 1, 0]]
        neighbors = self.maze.get_valid_neighbors((1, 1))
        self.assertEqual(set(neighbors), {(0, 1), (1, 0), (1, 2), (2, 1)})

class TestZombie(unittest.TestCase):
    def setUp(self):
        self.zombie = Zombie((0, 0))

    def test_zombie_initialization(self):
        self.assertEqual(self.zombie.grid_position, (0, 0))
        self.assertEqual(self.zombie.rect.size, (ZOMBIE_SIZE, ZOMBIE_SIZE))

    def test_zombie_move(self):
        self.zombie.move_to((1, 0))
        self.assertEqual(self.zombie.target_grid_position, (1, 0))

class TestGame(unittest.TestCase):
    @patch('pygame.display.set_mode')
    def setUp(self, mock_set_mode):
        self.screen = mock_set_mode.return_value
        self.screen.get_size.return_value = (800, 600)  # Mock the screen size
        self.game = Game(self.screen)

    def test_game_initialization(self):
        self.assertIsNotNone(self.game.player)
        self.assertIsNotNone(self.game.maze)
        self.assertEqual(self.game.state, "welcome")  # The initial state is "welcome"

    @patch('ezm.game.Game.handle_player_movement')
    @patch('ezm.game.Game.check_collisions')
    @patch('ezm.game.Game.spawn_zombies')
    @patch('ezm.game.Game.update_score')
    @patch('ezm.game.Game.check_game_over')
    @patch('ezm.game.Game.draw')
    def test_game_update_gameplay(self, mock_draw, mock_check_game_over, mock_update_score, 
                                  mock_spawn_zombies, mock_check_collisions, mock_handle_player_movement):
        self.game.state = "playing"
        result = self.game.update_gameplay()
        self.assertTrue(result)
        mock_handle_player_movement.assert_called()
        mock_check_collisions.assert_called_once()
        mock_spawn_zombies.assert_called_once()
        mock_update_score.assert_called_once()
        mock_check_game_over.assert_called_once()
        mock_draw.assert_called_once()

if __name__ == '__main__':
    unittest.main()