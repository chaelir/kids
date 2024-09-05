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
        self.assertEqual(self.player.grid_position, (0, 0))
        self.assertEqual(self.player.rect.size, (PLAYER_SIZE, PLAYER_SIZE))
        self.assertFalse(self.player.has_sword)

    def test_player_move(self):
        self.player.move((1, 0))
        self.assertEqual(self.player.grid_position, (1, 0))

    def test_player_pickup_sword(self):
        self.player.pickup_sword()
        self.assertTrue(self.player.has_sword)

class TestMaze(unittest.TestCase):
    def setUp(self):
        self.maze = Maze(10, 10)

    def test_maze_initialization(self):
        self.assertEqual(len(self.maze.grid), 10)
        self.assertEqual(len(self.maze.grid[0]), 10)

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
        self.assertEqual(self.zombie.rect.size, (CELL_SIZE, CELL_SIZE))

    def test_zombie_move(self):
        self.zombie.move_to((1, 0))
        self.assertEqual(self.zombie.target_grid_position, (1, 0))

class TestGame(unittest.TestCase):
    @patch('pygame.display.set_mode')
    def setUp(self, mock_set_mode):
        self.screen = mock_set_mode.return_value
        self.game = Game(self.screen)

    def test_game_initialization(self):
        self.assertIsNotNone(self.game.player)
        self.assertIsNotNone(self.game.maze)
        self.assertEqual(self.game.state, "playing")

    @patch('ezm.game.Game.handle_events')
    @patch('ezm.game.Game.update')
    @patch('ezm.game.Game.draw')
    def test_game_update_gameplay(self, mock_draw, mock_update, mock_handle_events):
        self.game.update_gameplay()
        mock_handle_events.assert_called_once()
        mock_update.assert_called_once()
        mock_draw.assert_called_once()

if __name__ == '__main__':
    unittest.main()