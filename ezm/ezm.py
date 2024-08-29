import os
import sys
import pygame
import time
import json
from maze import Maze
import random
import importlib.util
import execjs
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('emz.env')

# Update the getenv function to use os.getenv directly
def getenv(key, default):
    return os.getenv(key, default)

# Change the working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Constants
SCREEN_WIDTH = int(getenv('SCREEN_WIDTH', '1024'))
SCREEN_HEIGHT = int(getenv('SCREEN_HEIGHT', '768'))
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_GRAY = (200, 200, 200)
ORANGE = (255, 165, 0)

MIN_MAZE_HEIGHT = int(getenv('MIN_MAZE_HEIGHT', '9'))
MAX_MAZE_HEIGHT = int(getenv('MAX_MAZE_HEIGHT', '99'))
MIN_MAZE_WIDTH = int(getenv('MIN_MAZE_WIDTH', '9'))
MAX_MAZE_WIDTH = int(getenv('MAX_MAZE_WIDTH', '99'))
MIN_ZOMBIE_DELAY = int(getenv('MIN_ZOMBIE_DELAY', '1'))
MAX_ZOMBIE_DELAY = int(getenv('MAX_ZOMBIE_DELAY', '9'))
TILE_SIZE = int(getenv('TILE_SIZE', '32'))

MAP_WIDTH = int(getenv('MAP_WIDTH', '800'))
MAP_HEIGHT = int(getenv('MAP_HEIGHT', '600'))

MAX_ZOMBIES = int(getenv('MAX_ZOMBIES', '2'))

# Default settings
DEFAULT_MAZE_WIDTH = int(getenv('DEFAULT_MAZE_WIDTH', '29'))
DEFAULT_MAZE_HEIGHT = int(getenv('DEFAULT_MAZE_HEIGHT', '29'))
DEFAULT_ZOMBIE_DELAY = int(getenv('DEFAULT_ZOMBIE_DELAY', '5'))
DEFAULT_ZOMBIE_SPEED_FAST = getenv('DEFAULT_ZOMBIE_SPEED_FAST', 'True').lower() == 'true'
DEFAULT_ZOMBIE_SPAWNING_ENABLED = getenv('DEFAULT_ZOMBIE_SPAWNING_ENABLED', 'True').lower() == 'true'
DEFAULT_GENERATION_ALGORITHM = getenv('DEFAULT_GENERATION_ALGORITHM', 'recursive_division')
DEFAULT_PLAYER_NAME = getenv('DEFAULT_PLAYER_NAME', 'Mario')

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=pos)
        self.has_sword = False

    def collect_sword(self):
        self.has_sword = True
        self.image.fill(YELLOW)  # Change color when sword is collected

class Zombie(pygame.sprite.Sprite):
    def __init__(self, grid_pos):
        super().__init__()
        self.grid_position = grid_pos  # (row, col)
        self.target_grid_position = self.grid_position
        self.move_progress = 0
        self.move_duration = 1  # 1 second per tile

    def update(self, dt):
        if self.grid_position != self.target_grid_position:
            self.move_progress += dt / self.move_duration
            if self.move_progress >= 1:
                self.grid_position = self.target_grid_position
                self.move_progress = 0

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

class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.margin = int(min(self.screen_width, self.screen_height) * 0.02)  # 2% of smaller dimension
        self.legend_width = int(self.screen_width * 0.2)  # 20% of screen width
        self.maze_area_width = self.screen_width - 2 * self.margin - self.legend_width
        self.maze_area_height = self.screen_height - 2 * self.margin
        self.offset_x = self.margin
        self.offset_y = self.margin
        self.cell_size = None

        self.leaderboard = self.load_leaderboard()
        self.maze = None
        self.player_position = None
        self.zombies = pygame.sprite.Group()
        self.player_path = []
        self.tentative_path = []
        self.valid_moves = set()
        self.game_finished = False
        self.game_message = ""
        self.zombie_spawn_start_time = None
        self.zombies_vanquished = 0

        pygame.font.init()
        self.font = pygame.font.Font(None, int(min(self.screen_width, self.screen_height) * 0.03))
        self.title_font = pygame.font.Font(None, int(min(self.screen_width, self.screen_height) * 0.05))

        self.ZOMBIE_UPDATE_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ZOMBIE_UPDATE_EVENT, 200)  # Update every 200ms

        self.state = "welcome"
        print(f"Game initialized. Initial state: {self.state}")
        self.settings = {
            "maze_width": int(DEFAULT_MAZE_WIDTH),
            "maze_height": int(DEFAULT_MAZE_HEIGHT),
            "zombie_delay": int(DEFAULT_ZOMBIE_DELAY),
            "zombie_speed_fast": DEFAULT_ZOMBIE_SPEED_FAST,
            "zombie_spawning_enabled": DEFAULT_ZOMBIE_SPAWNING_ENABLED,
            "generation_algorithm": DEFAULT_GENERATION_ALGORITHM,
            "show_trail": False,
            "show_solution": False
        }
        self.player_name = getenv('DEFAULT_PLAYER_NAME', 'Mario')
        self.input_boxes = {
            "player": pygame.Rect(0, 0, 200, 32),
            "maze_width": pygame.Rect(0, 0, 60, 32),
            "maze_height": pygame.Rect(0, 0, 60, 32),
            "zombie_delay": pygame.Rect(0, 0, 60, 32)
        }
        self.active_input = "player"  # Set initial active input to player name

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        self.maze_generation_algorithm = 'backtracking'
        self.cursor_size = 3

        self.cursor = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.cursor, (255, 0, 0, 128), (7, 7), 7)
        pygame.mouse.set_visible(False)

        self.last_move_time = 0
        self.move_delay = 0.1  # 200 milliseconds delay between moves

        self.sword_position = None
        self.sword_collected = False
        self.sword_image = pygame.image.load(os.path.join("assets", "sword.jpg"))
        self.sword_image = pygame.transform.scale(self.sword_image, (TILE_SIZE, TILE_SIZE))

        self.player_image = pygame.image.load(os.path.join("assets", "nobody.jpg"))
        self.player_image = pygame.transform.scale(self.player_image, (TILE_SIZE, TILE_SIZE))
        self.player_with_sword_image = pygame.image.load(os.path.join("assets", "sworded.jpg"))
        self.player_with_sword_image = pygame.transform.scale(self.player_with_sword_image, (TILE_SIZE, TILE_SIZE))
        self.current_player_image = self.player_image

        self.zombie_image = pygame.image.load(os.path.join("assets", "zombie.jpg"))
        self.zombie_image = pygame.transform.scale(self.zombie_image, (TILE_SIZE, TILE_SIZE))

        self.clock = pygame.time.Clock()

        self.player_color = ORANGE
        self.trail_color = MAGENTA
        self.in_color = GREEN
        self.out_color = BLUE

        self.zombie_move_time = 0
        self.zombie_move_delay = 1  # Adjust this value to change zombie speed (higher = slower)

        self.maze_algorithms = {}
        self.load_maze_algorithms()
        self.current_algorithm = 'backtracking'  # Default algorithm

        self.show_trail = False  # Changed from True to False
        self.show_solution = False
        self.solution_color = (255, 215, 0)  # Gold color for solution

        print(f"Initial generation algorithm: {self.settings['generation_algorithm']}")
        print(f"Initial game state: {self.state}")  # Add this line

        # Load asset images for the welcome screen
        self.sword_welcome_image = pygame.image.load(os.path.join("assets", "sword.jpg"))
        self.player_welcome_image = pygame.image.load(os.path.join("assets", "nobody.jpg"))
        self.player_with_sword_welcome_image = pygame.image.load(os.path.join("assets", "sworded.jpg"))
        self.zombie_welcome_image = pygame.image.load(os.path.join("assets", "zombie.jpg"))

        # Scale the images to a suitable size for the welcome screen
        welcome_image_size = (100, 100)
        self.sword_welcome_image = pygame.transform.scale(self.sword_welcome_image, welcome_image_size)
        self.player_welcome_image = pygame.transform.scale(self.player_welcome_image, welcome_image_size)
        self.player_with_sword_welcome_image = pygame.transform.scale(self.player_with_sword_welcome_image, welcome_image_size)
        self.zombie_welcome_image = pygame.transform.scale(self.zombie_welcome_image, welcome_image_size)

        # Draw the welcome screen immediately
        self.draw_welcome_screen()
        pygame.display.flip()

        self.last_zombie_spawn_time = 0

    def load_leaderboard(self):
        try:
            with open('leaderboard.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def load_maze_algorithms(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        algorithm_dir = os.path.join(current_dir, "mazeai")
        print(f"Searching for algorithms in directory: {algorithm_dir}")
        for filename in os.listdir(algorithm_dir):
            if filename.endswith('.js'):
                algorithm_name = filename[:-3].replace('-', '_')  # Remove .js and replace - with _
                file_path = os.path.join(algorithm_dir, filename)
                with open(file_path, 'r') as file:
                    js_code = file.read()
                try:
                    ctx = execjs.compile(js_code)
                    self.maze_algorithms[algorithm_name] = ctx
                except Exception as e:
                    print(f"Error loading algorithm {algorithm_name}: {str(e)}")
                    print(f"JavaScript code causing the error:\n{js_code}")
        print(f"Loaded algorithms: {list(self.maze_algorithms.keys())}")

    def change_algorithm(self, algorithm_name):
        if algorithm_name in self.maze_algorithms:
            self.settings["generation_algorithm"] = algorithm_name
        else:
            print(f"Algorithm {algorithm_name} not found.")

    # Game initialization and state management
    def start_game(self):
        errors = self.validate_settings()
        if errors:
            print("Invalid settings:")
            for error in errors:
                print(error)
            return
        
        print(f"Available algorithms: {list(self.maze_algorithms.keys())}")
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                algorithm = self.settings["generation_algorithm"]
                print(f"Attempting to use algorithm: {algorithm}")
                self.maze = Maze(self.settings["maze_height"], self.settings["maze_width"], algorithm)
                if self.maze.solution:
                    print(f"Maze generated successfully on attempt {attempt + 1}")
                    break
                else:
                    raise ValueError("Generated maze has no solution")
            except Exception as e:
                print(f"Error generating maze (attempt {attempt + 1}): {str(e)}")
        else:
            print(f"Failed to generate a valid maze after {max_attempts} attempts. Using fallback method.")
            self.maze = Maze(self.settings["maze_height"], self.settings["maze_width"], "fallback")

        # Only proceed if maze generation was successful
        if self.maze:
            self.player_position = self.maze.in_point
            print(f"Initial player position: {self.player_position}")
            self.zombies = pygame.sprite.Group()
            self.player_path = [self.player_position]
            self.tentative_path = []
            self.game_finished = False
            self.game_message = ""
            self.state = "playing"
            print(f"Game started. New state: {self.state}")
            self.zombie_spawn_start_time = time.time() + self.settings["zombie_delay"]
            print(f"Zombie spawn start time set to: {self.zombie_spawn_start_time}")
            self.zombies_vanquished = 0
            self.calculate_maze_dimensions()
            self.spawn_sword()
            self.sword_collected = False  # Reset sword collection status
            print(f"Sword spawned at {self.sword_position}")
            self.update_zombie_timer()
            self.player_sprite = Player(self.player_position)
            self.spawn_initial_zombies()  # New method to spawn initial zombies
        else:
            print("Maze generation failed. Returning to welcome screen.")
            self.state = "welcome"
            print(f"State changed to: {self.state}")
            self.zombie_spawn_start_time = None

        print(f"Zombie spawning enabled: {self.settings['zombie_spawning_enabled']}")
        print(f"Zombie delay: {self.settings['zombie_delay']}")
        print(f"Max zombies: {MAX_ZOMBIES}")

        self.last_zombie_spawn_time = time.time()

    def spawn_sword(self):
        empty_cells = [(r, c) for r in range(self.maze.rows) for c in range(self.maze.cols) 
                       if self.maze.grid[r][c] == 0 and (r, c) != self.player_position
                       and (r, c) != self.maze.out_point]
        if empty_cells:
            self.sword_position = random.choice(empty_cells)
            print(f"Sword spawned at {self.sword_position}")
        else:
            print("No empty cells available for sword spawning")

    def spawn_initial_zombies(self):
        for _ in range(MAX_ZOMBIES):
            new_pos = self.get_random_empty_position()
            if new_pos:
                new_zombie = Zombie(new_pos)
                self.zombies.add(new_zombie)
                print(f"Initial zombie spawned at grid position: {new_pos}")
            else:
                print("No empty position found for zombie spawning")

    def spawn_zombies(self):
        # This method is now empty or can be removed
        pass

    def update_zombie_timer(self):
        interval = int(self.settings["zombie_delay"] * 1000 * (0.5 if self.settings["zombie_speed_fast"] else 1))
        pygame.time.set_timer(self.ZOMBIE_UPDATE_EVENT, interval)

    def game_over(self, message):
        self.state = "game_over"
        print(f"Game over. New state: {self.state}")
        self.game_message = message
        score = self.calculate_score()
        if self.player_position == self.maze.out_point:  # Success scenario
            score *= 2  # Double the score for successful escape
        self.update_leaderboard(score)
        self.draw_score_board()

    # Drawing methods
    def draw(self):
        self.screen.fill(WHITE)
        
        if self.state == "welcome":
            self.draw_welcome_screen()
        elif self.state == "playing":
            if self.maze:
                self.draw_maze()
                self.draw_player()
                self.draw_legend()
            else:
                error_text = "Maze generation failed. Press ESC to return to the welcome screen."
                error_surface = self.font.render(error_text, True, RED)
                error_rect = error_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(error_surface, error_rect)
        elif self.state == "game_over":
            self.draw_score_board()

        # Draw custom cursor
        mouse_pos = pygame.mouse.get_pos()
        self.screen.blit(self.cursor, (mouse_pos[0] - 7, mouse_pos[1] - 7))
        
        pygame.display.flip()

    def draw_welcome_screen(self):
        self.screen.fill(BLACK)

        title = self.title_font.render("Welcome to EscapeZombieMazia!", True, RED)
        title_rect = title.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title, title_rect)

        # Display validation warnings
        errors = self.validate_settings()
        if errors:
            warning_text = ", ".join(errors)
            warning_surface = self.font.render(warning_text, True, (255, 165, 0))  # Golden orange color
            warning_rect = warning_surface.get_rect(center=(self.screen_width // 2, title_rect.bottom + 30))
            self.screen.blit(warning_surface, warning_rect)

        # Define subpane areas
        rules_pane = pygame.Rect(50, 100, self.screen_width // 2 - 75, self.screen_height - 200)
        controls_pane = pygame.Rect(self.screen_width // 2 + 25, 100, self.screen_width // 2 - 75, self.screen_height - 200)

        # Draw subpanes
        pygame.draw.rect(self.screen, (50, 50, 50), rules_pane)
        pygame.draw.rect(self.screen, (50, 50, 50), controls_pane)

        # Game Rules
        rules_title = self.title_font.render("Game Rules", True, WHITE)
        self.screen.blit(rules_title, (rules_pane.x + 10, rules_pane.y + 10))

        rules = [
            "1. Navigate through the maze to reach the exit.",
            "2. Avoid zombies that spawn randomly",
            "   unless you have the sword.",
            "3. Use arrow keys to move.",
            "4. Game over if caught by zombies.",
            "5. Score based on maze size and zombie speed.",
        ]

        algorithms = [
            "Recursive Division", "Backtracking", "Hunt and Kill",
            "Wilson's", "Eller's", "Kruskal's", "Aldous-Broder",
            "Sidewinder", "Binary Tree", "Prim's"
        ]

        # Draw rules
        y_offset = 50
        for rule in rules:
            rule_surface = self.font.render(rule, True, WHITE)
            self.screen.blit(rule_surface, (rules_pane.x + 10, rules_pane.y + y_offset))
            y_offset += 30

        # Draw algorithms
        algo_title = self.font.render("6. Choose a maze generation algorithm:", True, WHITE)
        self.screen.blit(algo_title, (rules_pane.x + 10, rules_pane.y + y_offset))
        y_offset += 30

        for i, algo in enumerate(algorithms):
            algo_surface = self.font.render(f"   - {algo}", True, WHITE)
            x = rules_pane.x + 10 + (i % 2) * (rules_pane.width // 2)
            y = rules_pane.y + y_offset + (i // 2) * 30
            self.screen.blit(algo_surface, (x, y))

        # Display asset images
        welcome_image_size = (80, 80)
        image_spacing = 20
        images_start_y = rules_pane.bottom - welcome_image_size[1] - 40
        images = [
            (self.player_welcome_image, "Player"),
            (self.sword_welcome_image, "Sword"),
            (self.player_with_sword_welcome_image, "Sworded"),
            (self.zombie_welcome_image, "Zombie")
        ]
        for i, (image, label) in enumerate(images):
            x = rules_pane.x + 10 + i * (welcome_image_size[0] + image_spacing)
            y = images_start_y
            self.screen.blit(pygame.transform.scale(image, welcome_image_size), (x, y))
            label_surface = self.font.render(label, True, WHITE)
            label_rect = label_surface.get_rect(center=(x + welcome_image_size[0] // 2, y + welcome_image_size[1] + 20))
            self.screen.blit(label_surface, label_rect)

        # Game Controls
        controls_title = self.title_font.render("Game Controls", True, WHITE)
        self.screen.blit(controls_title, (controls_pane.x + 10, controls_pane.y + 10))

        y = controls_pane.y + 50
        for i, setting in enumerate(["player", "maze_width", "maze_height", "zombie_delay"]):
            text = f"{i+1}. {setting.replace('_', ' ').title()}: "
            setting_surface = self.font.render(text, True, WHITE)
            self.screen.blit(setting_surface, (controls_pane.x + 10, y))
            
            input_box = self.input_boxes[setting]
            input_box.topleft = (controls_pane.x + 180, y - 5)
            if self.active_input == setting:
                pygame.draw.rect(self.screen, YELLOW, input_box, 2)  # Use YELLOW for active input
            else:
                pygame.draw.rect(self.screen, LIGHT_GRAY, input_box, 2)
            
            # Display the current value in the input box
            if setting == "player":
                value = self.player_name if self.player_name else ""
            else:
                value = str(self.settings.get(setting, ""))
            
            value_surface = self.font.render(value, True, WHITE)
            self.screen.blit(value_surface, (input_box.x + 5, input_box.y + 5))
            
            if setting == "zombie_delay":
                unit_surface = self.font.render("s", True, WHITE)
                self.screen.blit(unit_surface, (input_box.right + 5, input_box.y + 5))
                range_text = f"({MIN_ZOMBIE_DELAY}-{MAX_ZOMBIE_DELAY})"
                range_surface = self.font.render(range_text, True, LIGHT_GRAY)
                self.screen.blit(range_surface, (input_box.right + 25, input_box.y + 5))
            elif setting != "player":
                range_text = f"({MIN_MAZE_WIDTH}-{MAX_MAZE_WIDTH})"
                range_surface = self.font.render(range_text, True, LIGHT_GRAY)
                self.screen.blit(range_surface, (input_box.right + 10, input_box.y + 5))
            
            y += 50

        toggle_settings = [
            ("Zombie Speed", "zombie_speed_fast", "F1"),
            ("Zombie Spawning", "zombie_spawning_enabled", "F2"),
            ("Show Trail", "show_trail", "F3"),
            ("Show Solution", "show_solution", "F4")
        ]

        for text, setting, key in toggle_settings:
            toggle_text = f"{text}: {'ON' if self.settings.get(setting, False) else 'OFF'}"
            toggle_surface = self.font.render(toggle_text, True, WHITE)
            toggle_rect = toggle_surface.get_rect(topleft=(controls_pane.x + 10, y))
            self.screen.blit(toggle_surface, toggle_rect)
            pygame.draw.rect(self.screen, WHITE, toggle_rect.inflate(10, 10), 1)  # Draw border around toggle button
            toggle_key = self.font.render(f"Press {key} to toggle", True, LIGHT_GRAY)
            self.screen.blit(toggle_key, (controls_pane.x + 10, y + 30))
            y += 70

        algo_text = f"Generation Algorithm: {self.settings.get('generation_algorithm', '')}"
        algo_surface = self.font.render(algo_text, True, WHITE)
        algo_rect = algo_surface.get_rect(topleft=(controls_pane.x + 10, y))
        self.screen.blit(algo_surface, algo_rect)
        pygame.draw.rect(self.screen, WHITE, algo_rect.inflate(10, 10), 1)  # Draw border around algorithm button
        algo_key = self.font.render("Press F5 to change", True, LIGHT_GRAY)
        self.screen.blit(algo_key, (controls_pane.x + 10, y + 30))

        start_text = self.font.render("Start Game", True, WHITE)
        start_rect = start_text.get_rect(center=(self.screen_width // 2, self.screen_height - 60))
        pygame.draw.rect(self.screen, GREEN, start_rect.inflate(20, 10))
        self.screen.blit(start_text, start_rect)

        # Add this print statement at the end of the method
        print(f"End of draw_welcome_screen. Active input is: {self.active_input}")
        print(f"Current player name: {self.player_name}")

    def draw_legend(self):
        legend_x = self.screen_width - self.legend_width
        legend_y = self.margin
        legend_height = self.screen_height - 2 * self.margin

        pygame.draw.rect(self.screen, WHITE, (legend_x, legend_y, self.legend_width, legend_height))
        pygame.draw.rect(self.screen, BLACK, (legend_x, legend_y, self.legend_width, legend_height), 2)

        title_surface = self.title_font.render("Map Guide", True, BLACK)
        title_rect = title_surface.get_rect(center=(legend_x + self.legend_width // 2, legend_y + 25))
        self.screen.blit(title_surface, title_rect)

        legend_items = [
            ("Player", ORANGE),
            ("Trail", MAGENTA),
            ("Walls", BLACK),
            ("Zombies", RED),
            ("IN", GREEN),
            ("OUT", BLUE),
            ("Sword", YELLOW)
        ]
        for i, (text, color) in enumerate(legend_items[:-1]):  # Exclude the last item (Sword)
            pygame.draw.rect(self.screen, color, (legend_x + 10, legend_y + 60 + i*30, 20, 20))
            text_surface = self.font.render(text, True, color)
            self.screen.blit(text_surface, (legend_x + 40, legend_y + 60 + i*30))

        if self.state == "playing" and self.maze:
            info_text = [
                f"Maze Size: {self.maze.rows}x{self.maze.cols}",
                f"Solution Length: {self.maze.get_solution_length()}",
                f"Zombie Delay: {self.settings.get('zombie_delay', 0)}s",
                f"Zombie Speed: {'Fast' if self.settings.get('zombie_speed_fast', False) else 'Slow'}",
                f"Spawning: {'ON' if self.settings.get('zombie_spawning_enabled', False) else 'OFF'}",
                f"Sword: {'Collected' if self.sword_collected else 'Not Collected'}",
                f"Zombies Vanquished: {self.zombies_vanquished}",
                f"Show Trail: {'ON' if self.settings.get('show_trail', False) else 'OFF'}",
                f"Show Solution: {'ON' if self.settings.get('show_solution', False) else 'OFF'}"
            ]
            for i, text in enumerate(info_text):
                info_surface = self.font.render(text, True, BLACK)
                self.screen.blit(info_surface, (legend_x + 10, legend_y + 240 + i * 30))
        elif self.state == "playing":
            error_text = "Maze generation failed. Please restart the game."
            error_surface = self.font.render(error_text, True, RED)
            self.screen.blit(error_surface, (legend_x + 10, legend_y + 240))

    def draw_maze(self):
        if not self.maze or self.cell_size is None:
            return  # Don't try to draw if maze doesn't exist or cell_size is not set

        self.calculate_maze_dimensions()  # Ensure cell_size is set

        maze_rect = pygame.Rect(self.offset_x, self.offset_y, 
                               self.cell_size * self.maze.cols, 
                               self.cell_size * self.maze.rows)
        pygame.draw.rect(self.screen, WHITE, maze_rect)
        pygame.draw.rect(self.screen, BLACK, maze_rect, 2)  # Border

        for row in range(self.maze.rows):
            for col in range(self.maze.cols):
                x = self.offset_x + col * self.cell_size
                y = self.offset_y + row * self.cell_size
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                if self.maze.is_wall(row, col):
                    pygame.draw.rect(self.screen, BLACK, cell_rect)

        # Draw IN point
        in_rect = pygame.Rect(self.offset_x + self.maze.in_point[1] * self.cell_size,
                              self.offset_y + self.maze.in_point[0] * self.cell_size,
                              self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, self.in_color, in_rect)
        
        # Draw OUT point
        out_rect = pygame.Rect(self.offset_x + self.maze.out_point[1] * self.cell_size,
                               self.offset_y + self.maze.out_point[0] * self.cell_size,
                               self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, self.out_color, out_rect)

        # Draw the sword if not collected
        if not self.sword_collected and self.sword_position:
            sword_x = self.offset_x + self.sword_position[1] * self.cell_size
            sword_y = self.offset_y + self.sword_position[0] * self.cell_size
            self.screen.blit(pygame.transform.scale(self.sword_image, (self.cell_size, self.cell_size)), (sword_x, sword_y))

        # Draw solution if enabled
        if self.settings.get('show_solution', False) and self.maze.solution:
            solution_points = [(self.offset_x + col * self.cell_size + self.cell_size // 2,
                                self.offset_y + row * self.cell_size + self.cell_size // 2)
                               for row, col in self.maze.solution]
            pygame.draw.lines(self.screen, self.solution_color, False, solution_points, 2)

        # Draw player trail if enabled
        if self.settings.get('show_trail', False) and len(self.player_path) > 1:
            trail_points = [(self.offset_x + col * self.cell_size + self.cell_size // 2,
                             self.offset_y + row * self.cell_size + self.cell_size // 2)
                            for row, col in self.player_path]
            pygame.draw.lines(self.screen, self.trail_color, False, trail_points, 2)

        # Draw zombies
        for zombie in self.zombies:
            pos = zombie.get_current_position()
            zombie_x = self.offset_x + pos[1] * self.cell_size
            zombie_y = self.offset_y + pos[0] * self.cell_size
            self.screen.blit(pygame.transform.scale(self.zombie_image, (self.cell_size, self.cell_size)), (zombie_x, zombie_y))

    def draw_player(self):
        if self.player_position:
            player_x = self.offset_x + self.player_position[1] * self.cell_size
            player_y = self.offset_y + self.player_position[0] * self.cell_size
            player_image = self.player_with_sword_image if self.sword_collected else self.player_image
            self.screen.blit(pygame.transform.scale(player_image, (self.cell_size, self.cell_size)), (player_x, player_y))

    def draw_score_board(self):
        # Dark background
        self.screen.fill((20, 20, 20))  # Very dark gray

        # Title
        if self.player_position == self.maze.out_point:
            title = self.title_font.render("Success! You Escaped!", True, GREEN)
        else:
            title = self.title_font.render("Game Over", True, RED)
        title_rect = title.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title, title_rect)

        # Score display (always show, even if zero)
        score = self.calculate_score()
        score_text = self.font.render(f"Your Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(score_text, score_rect)

        # Leaderboard
        leaderboard_title = self.title_font.render("Leaderboard", True, GREEN)  # Changed to GREEN
        leaderboard_title_rect = leaderboard_title.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(leaderboard_title, leaderboard_title_rect)

        y = 200
        for i, (name, score) in enumerate(self.leaderboard[:10], 1):
            if i == 1:
                color = (255, 215, 0)  # Gold
            elif i == 2:
                color = (192, 192, 192)  # Silver
            elif i == 3:
                color = (205, 127, 50)  # Copper
            else:
                color = WHITE

            text = self.font.render(f"{i}. {name}: {score}", True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, y))
            self.screen.blit(text, text_rect)
            y += 40

        # Instructions
        instructions = self.font.render("Press Enter to Replay or ESC for Welcome Screen", True, LIGHT_GRAY)
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
        self.screen.blit(instructions, instructions_rect)

    def validate_settings(self):
        errors = []
        if not self.player_name or not self.player_name.strip():
            errors.append("Please enter a valid player name.")
        if not (MIN_MAZE_WIDTH <= self.settings["maze_width"] <= MAX_MAZE_WIDTH):
            errors.append(f"Maze width must be between {MIN_MAZE_WIDTH} and {MAX_MAZE_WIDTH}.")
        if not (MIN_MAZE_HEIGHT <= self.settings["maze_height"] <= MAX_MAZE_HEIGHT):
            errors.append(f"Maze height must be between {MIN_MAZE_HEIGHT} and {MAX_MAZE_HEIGHT}.")
        if not (MIN_ZOMBIE_DELAY <= self.settings["zombie_delay"] <= MAX_ZOMBIE_DELAY):
            errors.append(f"Zombie delay must be between {MIN_ZOMBIE_DELAY} and {MAX_ZOMBIE_DELAY}.")
        if self.settings["generation_algorithm"] not in self.maze_algorithms:
            errors.append(f"Invalid maze generation algorithm: {self.settings['generation_algorithm']}")
        return errors

    # Event handling methods
    def handle_welcome_click(self, pos):
        print(f"Welcome click at position: {pos}")
        for setting, box in self.input_boxes.items():
            if box.collidepoint(pos):
                self.active_input = setting
                print(f"Activated input box: {setting}")
                return

        # Check for clicks on toggle buttons
        y = self.input_boxes["zombie_delay"].bottom + 20
        toggle_settings = [
            ("zombie_speed_fast", "F1"),
            ("zombie_spawning_enabled", "F2"),
            ("show_trail", "F3"),
            ("show_solution", "F4")
        ]
        for setting, key in toggle_settings:
            if pygame.Rect(self.input_boxes["player"].left, y, 200, 30).collidepoint(pos):
                self.settings[setting] = not self.settings.get(setting, False)
                print(f"Toggled {setting}: {self.settings[setting]}")
                break
            y += 70

        # Check for click on algorithm change button
        if pygame.Rect(self.input_boxes["player"].left, y, 200, 30).collidepoint(pos):
            algorithms = list(self.maze_algorithms.keys())
            current_index = algorithms.index(self.settings.get("generation_algorithm", algorithms[0]))
            next_index = (current_index + 1) % len(algorithms)
            self.settings["generation_algorithm"] = algorithms[next_index]
            print(f"Changed algorithm to: {self.settings['generation_algorithm']}")

        # Check for click on start game button
        start_button_rect = pygame.Rect(self.screen_width // 2 - 100, self.screen_height - 50, 200, 40)
        if start_button_rect.collidepoint(pos):
            print("Current settings before starting game:")
            for key, value in self.settings.items():
                print(f"{key}: {value}")
            errors = self.validate_settings()
            if not errors:
                print("Starting game...")
                self.start_game()
                self.state = "playing"  # Immediately change the state
                print(f"Game started. New state: {self.state}")
            else:
                print("Invalid settings. Please check and try again.")
                for error in errors:
                    print(error)

        self.draw_welcome_screen()
        pygame.display.flip()

    def handle_welcome_keydown(self, event):
        print(f"Welcome keydown: {pygame.key.name(event.key)}")
        if event.key == pygame.K_ESCAPE:
            print("Escape key pressed on welcome screen. Quitting the game.")
            pygame.quit()
            sys.exit()
        elif event.key == pygame.K_RETURN:
            print("Current settings before starting game:")
            for key, value in self.settings.items():
                print(f"{key}: {value}")
            errors = self.validate_settings()
            if not errors:
                print("Starting game...")
                self.start_game()
                self.state = "playing"  # Immediately change the state
                print(f"Game started. New state: {self.state}")
            else:
                print("Invalid settings. Please check and try again.")
                for error in errors:
                    print(error)
        elif event.key == pygame.K_TAB:
            # Cycle through input boxes
            input_boxes = list(self.input_boxes.keys())
            current_index = input_boxes.index(self.active_input) if self.active_input else -1
            self.active_input = input_boxes[(current_index + 1) % len(input_boxes)]
            print(f"Active input changed to: {self.active_input}")
        elif event.key == pygame.K_F1:
            self.settings["zombie_speed_fast"] = not self.settings.get("zombie_speed_fast", False)
            print(f"Zombie speed toggled: {'fast' if self.settings['zombie_speed_fast'] else 'normal'}")
        elif event.key == pygame.K_F2:
            self.settings["zombie_spawning_enabled"] = not self.settings.get("zombie_spawning_enabled", False)
            print(f"Zombie spawning toggled: {'enabled' if self.settings['zombie_spawning_enabled'] else 'disabled'}")
        elif event.key == pygame.K_F3:
            self.settings["show_trail"] = not self.settings.get("show_trail", False)
            print(f"Trail display toggled: {'enabled' if self.settings['show_trail'] else 'disabled'}")
        elif event.key == pygame.K_F4:
            self.settings["show_solution"] = not self.settings.get("show_solution", False)
            print(f"Solution display toggled: {'enabled' if self.settings['show_solution'] else 'disabled'}")
        elif event.key == pygame.K_F5:
            algorithms = list(self.maze_algorithms.keys())
            current_index = algorithms.index(self.settings.get("generation_algorithm", algorithms[0]))
            next_index = (current_index + 1) % len(algorithms)
            self.settings["generation_algorithm"] = algorithms[next_index]
            print(f"Changed algorithm to: {self.settings['generation_algorithm']}")
        elif event.key == pygame.K_BACKSPACE:
            if self.active_input == "player":
                self.player_name = self.player_name[:-1]
            elif self.active_input in ["maze_width", "maze_height", "zombie_delay"]:
                current_value = str(self.settings[self.active_input])
                self.settings[self.active_input] = int(current_value[:-1]) if current_value[:-1] else 0
        elif event.unicode.isprintable():
            if self.active_input == "player":
                self.player_name += event.unicode
            elif self.active_input in ["maze_width", "maze_height", "zombie_delay"]:
                current_value = str(self.settings[self.active_input])
                new_value = current_value + event.unicode
                if new_value.isdigit():
                    self.settings[self.active_input] = int(new_value)

        print(f"After input processing:")
        print(f"Active input: {self.active_input}")
        print(f"Player name: {self.player_name}")
        print(f"Settings: {self.settings}")

        # Redraw the welcome screen to reflect changes
        self.draw_welcome_screen()
        pygame.display.flip()

        print(f"End of handle_welcome_keydown. Active input is now: {self.active_input}")
        print(f"Current player name: {self.player_name}")

    def replay_game(self):
        # Reset game state
        self.player_position = None
        self.zombies = pygame.sprite.Group()
        self.player_path = []
        self.tentative_path = []
        self.game_finished = False
        self.game_message = ""
        
        # Start a new game with the same settings
        self.start_game()
        print(f"Game replayed. New state: {self.state}")

    def update_gameplay(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.handle_keystroke(event.key)

        self.move_zombies()
        dt = self.clock.get_time() / 1000
        for zombie in self.zombies:
            zombie.update(dt)

        self.check_zombie_collisions()  # Add this line

        self.draw()
        pygame.display.flip()
        self.clock.tick(60)
        return True

    def handle_resize(self, size):
        self.screen_width, self.screen_height = size
        self.margin = int(min(self.screen_width, self.screen_height) * 0.02)
        self.legend_width = int(self.screen_width * 0.2)
        self.maze_area_width = self.screen_width - 2 * self.margin - self.legend_width
        self.maze_area_height = self.screen_height - 2 * self.margin
        self.offset_x = self.margin
        self.offset_y = self.margin
        self.font = pygame.font.Font(None, int(min(self.screen_width, self.screen_height) * 0.03))
        self.title_font = pygame.font.Font(None, int(min(self.screen_width, self.screen_height) * 0.05))
        self.calculate_maze_dimensions()

    # Helper methods
    def round_to_odd(self, value, min_value, max_value):
        return max(min_value, min(max_value, value + (value % 2 - 1)))

    def get_cell_from_pos(self, pos):
        x, y = pos
        row = (y - self.offset_y) // self.cell_size
        col = (x - self.offset_x) // self.cell_size
        if 0 <= row < self.maze.rows and 0 <= col < self.maze.cols:
            return row, col
        return None

    def get_valid_moves(self):
        valid_moves = set()
        for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # right, down, left, up
            current = self.player_position
            while True:
                next_cell = (current[0] + direction[0], current[1] + direction[1])
                if self.maze.is_wall(*next_cell) or next_cell[0] < 0 or next_cell[0] >= self.maze.rows or next_cell[1] < 0 or next_cell[1] >= self.maze.cols:
                    break
                valid_moves.add(next_cell)
                current = next_cell
        return valid_moves

    def update_valid_moves(self):
        self.valid_moves = self.get_valid_moves()

    def get_path_to_cell(self, target_cell):
        path = [self.player_position]
        current = self.player_position
        while current != target_cell:
            if target_cell[1] > current[1]:
                current = (current[0], current[1] + 1)
            elif target_cell[1] < current[1]:
                current = (current[0], current[1] - 1)
            elif target_cell[0] > current[0]:
                current = (current[0] + 1, current[1])
            elif target_cell[0] < current[0]:
                current = (current[0] - 1, current[1])
            path.append(current)
        return path

    def is_turn(self, path):
        if len(path) < 3:
            return False
        return (path[-1][0] - path[-2][0]) != (path[-2][0] - path[-3][0]) or \
               (path[-1][1] - path[-2][1]) != (path[-2][1] - path[-3][1])

    def is_valid_path(self, path):
        return all(self.maze.get_valid_neighbors(cell) for cell in path)

    def move_zombies(self):
        for zombie in self.zombies:
            if zombie.grid_position == zombie.target_grid_position:
                possible_moves = [
                    (zombie.grid_position[0] - 1, zombie.grid_position[1]),
                    (zombie.grid_position[0] + 1, zombie.grid_position[1]),
                    (zombie.grid_position[0], zombie.grid_position[1] - 1),
                    (zombie.grid_position[0], zombie.grid_position[1] + 1)
                ]
                valid_moves = [move for move in possible_moves if not self.maze.is_wall(*move)]
                
                if valid_moves:
                    new_pos = random.choice(valid_moves)
                    zombie.move_to(new_pos)
                    
                    # Check for collision immediately after moving
                    if new_pos == self.player_position:
                        self.handle_collision(zombie)

    def handle_collision(self, zombie):
        if self.sword_collected:
            self.zombies.remove(zombie)
            self.zombies_vanquished += 1
            print(f"Zombie vanquished! Total vanquished: {self.zombies_vanquished}")
        else:
            self.game_over("Game over! You were caught by a zombie.")

    def get_random_empty_position(self):
        empty_cells = [(r, c) for r in range(self.maze.rows) for c in range(self.maze.cols)
                       if self.maze.grid[r][c] == 0 and (r, c) != self.player_position
                       and (r, c) != self.maze.out_point and (r, c) != self.sword_position]
        return random.choice(empty_cells) if empty_cells else None

    def calculate_score(self):
        if not self.settings.get("zombie_spawning_enabled", False):
            return 0
        
        maze_difficulty = self.maze.rows * self.maze.cols
        zombie_time_factor = 10 / self.settings.get("zombie_delay", 0)
        speed_factor = 2 if self.settings.get("zombie_speed_fast", False) else 1
        return int(maze_difficulty * zombie_time_factor * speed_factor)

    def update_static_screen(self):
        redraw_needed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event detected")
                return False
            elif event.type == pygame.KEYDOWN:
                if self.state == "welcome" and event.key == pygame.K_ESCAPE:
                    print("Escape key pressed on welcome screen. Quitting the game.")
                    return False
                elif self.state == "welcome":
                    self.handle_welcome_keydown(event)
                    redraw_needed = True
                elif self.state == "game_over":
                    self.handle_game_over_keydown(event)
                    redraw_needed = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "welcome":
                    self.handle_welcome_click(event.pos)
                    redraw_needed = True

        if redraw_needed:
            self.draw()
            pygame.display.flip()
            print(f"Current state: {self.state}, Active input: {self.active_input}, Player name: {self.player_name}")

        return True

    # Leaderboard methods
    def update_leaderboard(self, score):
        self.leaderboard.append((self.player_name, score))
        self.leaderboard.sort(key=lambda x: x[1], reverse=True)
        self.leaderboard = self.leaderboard[:10]
        self.save_leaderboard()

    def save_leaderboard(self):
        try:
            with open('leaderboard.json', 'w') as f:
                json.dump(self.leaderboard, f)
        except IOError:
            print("Error saving leaderboard.")

    def calculate_maze_dimensions(self):
        available_width = self.maze_area_width
        available_height = self.maze_area_height

        cell_width = available_width // self.maze.cols
        cell_height = available_height // self.maze.rows

        self.cell_size = min(cell_width, cell_height)

        total_maze_width = self.cell_size * self.maze.cols
        total_maze_height = self.cell_size * self.maze.rows

        self.offset_x = self.margin + (available_width - total_maze_width) // 2
        self.offset_y = self.margin + (available_height - total_maze_height) // 2

    # Main game loop
    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                print("Quit event detected")
                return False
            elif event.type == pygame.KEYDOWN:
                if self.state == "welcome":
                    self.handle_welcome_keydown(event)
                elif self.state == "playing":
                    self.handle_keystroke(event.key)
                elif self.state == "game_over":
                    self.handle_game_over_keydown(event)
        return True

    def handle_keystroke(self, key):
        print(f"Keystroke in playing state: {pygame.key.name(key)}")
        if self.state != "playing" or not self.maze:
            print("Not in playing state or maze not generated")
            return

        if key == pygame.K_ESCAPE:
            print("Escaping to welcome screen")
            self.state = "welcome"
            self.draw_welcome_screen()
            return

        current_time = time.time()
        if current_time - self.last_move_time < self.move_delay:
            print("Move ignored due to delay")
            return

        move = {
            pygame.K_UP: (-1, 0),
            pygame.K_DOWN: (1, 0),
            pygame.K_LEFT: (0, -1),
            pygame.K_RIGHT: (0, 1)
        }.get(key)

        if move:
            new_row = self.player_position[0] + move[0]
            new_col = self.player_position[1] + move[1]
            new_pos = (new_row, new_col)
            
            if not self.maze.is_wall(new_row, new_col):
                self.player_position = new_pos
                self.player_path.append(new_pos)
                self.update_valid_moves()
                self.last_move_time = current_time
                print(f"Player moved to: {new_pos}")

                if self.player_position == self.sword_position and not self.sword_collected:
                    self.sword_collected = True
                    print("Sword collected!")

                self.check_zombie_collisions()  # Check for collisions after movement

                # Check if player has reached the exit
                if self.player_position == self.maze.out_point:
                    self.game_over("Congratulations! You've escaped the maze!")
                    return
            else:
                print("Move blocked by wall")
        elif key == pygame.K_F3:
            self.settings["show_trail"] = not self.settings.get("show_trail", False)
            print(f"Trail display toggled: {'enabled' if self.settings['show_trail'] else 'disabled'}")
        elif key == pygame.K_F4:
            self.settings["show_solution"] = not self.settings.get("show_solution", False)
            print(f"Solution display toggled: {'enabled' if self.settings['show_solution'] else 'disabled'}")
        elif key == pygame.K_F2:
            self.settings["zombie_spawning_enabled"] = not self.settings.get("zombie_spawning_enabled", False)
            print(f"Zombie spawning toggled: {'enabled' if self.settings['zombie_spawning_enabled'] else 'disabled'}")
        elif key == pygame.K_F1:
            self.settings["zombie_speed_fast"] = not self.settings.get("zombie_speed_fast", False)
            self.update_zombie_timer()
            print(f"Zombie speed toggled: {'fast' if self.settings['zombie_speed_fast'] else 'normal'}")

        print("Current settings:", self.settings)
        self.draw()  # Redraw the game after each action

    def check_zombie_collisions(self):
        for zombie in self.zombies:
            if zombie.grid_position == zombie.target_grid_position and zombie.grid_position == self.player_position:
                self.handle_collision(zombie)
                return

    def handle_game_over_keydown(self, event):
        if event.key == pygame.K_RETURN:
            print("Replaying game")
            self.replay_game()
        elif event.key == pygame.K_ESCAPE:
            print("Changing state to welcome")
            self.state = "welcome"
            print(f"State changed to: {self.state}")
            self.draw_welcome_screen()
        elif event.key == pygame.K_TAB:
            # Cycle through input boxes
            input_boxes = list(self.input_boxes.keys())
            current_index = input_boxes.index(self.active_input) if self.active_input else -1
            self.active_input = input_boxes[(current_index + 1) % len(input_boxes)]
            print(f"Active input changed to: {self.active_input}")
        return True

    def update(self):
        events = pygame.event.get()
        redraw_needed = False

        for event in events:
            if event.type == pygame.QUIT:
                print("Quit event detected")
                return False
            elif event.type == pygame.KEYDOWN:
                if self.state == "welcome":
                    self.handle_welcome_keydown(event)
                    redraw_needed = True
                elif self.state == "playing":
                    self.handle_keystroke(event.key)
                    redraw_needed = True
                elif self.state == "game_over":
                    self.handle_game_over_keydown(event)
                    redraw_needed = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "welcome":
                    self.handle_welcome_click(event.pos)
                    redraw_needed = True

        if self.state == "playing" and self.maze:
            self.move_zombies()
            dt = self.clock.get_time() / 1000
            for zombie in self.zombies:
                zombie.update(dt)
            redraw_needed = True

        if redraw_needed:
            self.draw()
            pygame.display.flip()

        self.clock.tick(60)  # Limit the frame rate to 60 FPS

        if redraw_needed:
            print(f"Current state: {self.state}, Active input: {self.active_input}, Player name: {self.player_name}")

        return True

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("EscapeZombieMazia")

    game = Game(screen)
    clock = pygame.time.Clock()
    running = True
    while running:
        if game.state == "playing":
            running = game.update_gameplay()
            clock.tick(30)
        else:
            running = game.update_static_screen()
        
        # Add a small delay to reduce CPU usage
         # Limits the frame rate to 30 FPS (frames per second) for static screens
        # The number 30 here represents the target frame rate.
        # It means the game loop will try to run 30 times per second.
        # This helps reduce CPU usage when displaying static content,
        # while still maintaining responsiveness.

    pygame.quit()
    sys.exit()
