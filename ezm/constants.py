import os
from dotenv import load_dotenv

# Load environment variables from ezm.env
load_dotenv('ezm.env')

def getenv(key, default):
    return os.getenv(key, default)

def parse_bool(value):
    return value.lower() == 'true'

def parse_int(value, default):
    try:
        return int(value)
    except ValueError:
        return default

# Screen dimensions
SCREEN_WIDTH = parse_int(getenv('SCREEN_WIDTH', '1024'), 1024)
SCREEN_HEIGHT = parse_int(getenv('SCREEN_HEIGHT', '768'), 768)

# Maze settings
MIN_MAZE_HEIGHT = parse_int(getenv('MIN_MAZE_HEIGHT', '9'), 9)
MAX_MAZE_HEIGHT = parse_int(getenv('MAX_MAZE_HEIGHT', '99'), 99)
MIN_MAZE_WIDTH = parse_int(getenv('MIN_MAZE_WIDTH', '9'), 9)
MAX_MAZE_WIDTH = parse_int(getenv('MAX_MAZE_WIDTH', '99'), 99)
MAZE_WIDTH = parse_int(getenv('DEFAULT_MAZE_WIDTH', '19'), 19)
MAZE_HEIGHT = parse_int(getenv('DEFAULT_MAZE_HEIGHT', '19'), 19)

# Zombie settings
MIN_ZOMBIE_DELAY = parse_int(getenv('MIN_ZOMBIE_DELAY', '1'), 1)
MAX_ZOMBIE_DELAY = parse_int(getenv('MAX_ZOMBIE_DELAY', '9'), 9)
DEFAULT_ZOMBIE_DELAY = parse_int(getenv('DEFAULT_ZOMBIE_DELAY', '1'), 1)
DEFAULT_ZOMBIE_SPEED_FAST = parse_bool(getenv('DEFAULT_ZOMBIE_SPEED_FAST', 'True'))
DEFAULT_ZOMBIE_SPAWNING_ENABLED = parse_bool(getenv('DEFAULT_ZOMBIE_SPAWNING_ENABLED', 'True'))
MAX_ZOMBIES = parse_int(getenv('MAX_ZOMBIES', '1'), 1)

# Player settings
DEFAULT_PLAYER_NAME = getenv('DEFAULT_PLAYER_NAME', 'Mario')

# Sword settings
MIN_SWORDS = parse_int(getenv('MIN_SWORDS', '1'), 1)
MAX_SWORDS = parse_int(getenv('MAX_SWORDS', '3'), 3)
DEFAULT_SWORD_COUNT = parse_int(getenv('DEFAULT_SWORD_COUNT', '1'), 1)

# Game settings
TILE_SIZE = parse_int(getenv('TILE_SIZE', '32'), 32)
MAP_WIDTH = parse_int(getenv('MAP_WIDTH', '800'), 800)
MAP_HEIGHT = parse_int(getenv('MAP_HEIGHT', '600'), 600)
DEFAULT_GENERATION_ALGORITHM = getenv('DEFAULT_GENERATION_ALGORITHM', 'recursive_division')

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_WIN = "win"

# Asset paths
ZOMBIE_IMAGE_PATH = "zombie.jpg"
SWORD_IMAGE_PATH = "sword.jpg"
PLAYER_IMAGE_PATH = "nobody.jpg"
PLAYER_WITH_SWORD_IMAGE_PATH = "sworded.jpg"

# Other constants that were in the original file but not in the env file
FPS = 60
CELL_SIZE = TILE_SIZE
PLAYER_SPEED = 5
PLAYER_SIZE = 20
ZOMBIE_SPEED = 3
ZOMBIE_SIZE = 30