import unittest
from unittest.mock import patch, MagicMock
import pygame
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ezm.main import initialize_game, main_game_loop, cleanup
from ezm.constants import FPS

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

if __name__ == '__main__':
    unittest.main()