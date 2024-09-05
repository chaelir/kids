import pygame
import time
import json
import random
import os
import execjs
from ezm.constants import *
from ezm.player import Player
from ezm.zombie import Zombie
from ezm.maze import Maze

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.initialize_game_variables()
        self.load_assets()
        self.load_maze_algorithms()
        self.font = pygame.font.Font(None, int(min(self.screen_width, self.screen_height) * 0.03))
        self.title_font = pygame.font.Font(None, int(min(self.screen_width, self.screen_height) * 0.05))
        self.start_game()  # Call start_game in the constructor

    def initialize_game_variables(self):
        self.state = "welcome"
        self.settings = {
            "maze_width": MAZE_WIDTH,
            "maze_height": MAZE_HEIGHT,
            "zombie_delay": DEFAULT_ZOMBIE_DELAY,
            "zombie_speed_fast": DEFAULT_ZOMBIE_SPEED_FAST,
            "zombie_spawning_enabled": DEFAULT_ZOMBIE_SPAWNING_ENABLED,
            "generation_algorithm": DEFAULT_GENERATION_ALGORITHM,
            "player_name": DEFAULT_PLAYER_NAME,
            "sword_count": DEFAULT_SWORD_COUNT
        }
        self.maze = None
        self.player = None
        self.zombies = pygame.sprite.Group()
        self.swords = pygame.sprite.Group()
        self.score = 0
        self.game_over = False
        self.start_time = None
        self.end_time = None
        self.leaderboard = self.load_leaderboard()
        self.zombies_vanquished = 0

    def load_leaderboard(self):
        try:
            with open("leaderboard.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def load_assets(self):
        # Update asset paths to use the 'ezm' folder
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets')
        self.player_image = pygame.image.load(os.path.join(asset_dir, "nobody.jpg")).convert_alpha()
        self.player_with_sword_image = pygame.image.load(os.path.join(asset_dir, "sworded.jpg")).convert_alpha()
        self.zombie_image = pygame.image.load(os.path.join(asset_dir, "zombie.jpg")).convert_alpha()
        self.sword_image = pygame.image.load(os.path.join(asset_dir, "sword.jpg")).convert_alpha()

        # Scale images to appropriate sizes
        tile_size = (TILE_SIZE, TILE_SIZE)
        self.player_image = pygame.transform.smoothscale(self.player_image, tile_size)
        self.player_with_sword_image = pygame.transform.smoothscale(self.player_with_sword_image, tile_size)
        self.zombie_image = pygame.transform.smoothscale(self.zombie_image, tile_size)
        self.sword_image = pygame.transform.smoothscale(self.sword_image, tile_size)

        self.current_player_image = self.player_image

        # Load and scale welcome screen images
        welcome_image_size = (100, 100)
        self.sword_welcome_image = pygame.transform.smoothscale(self.sword_image, welcome_image_size)
        self.player_welcome_image = pygame.transform.smoothscale(self.player_image, welcome_image_size)
        self.player_with_sword_welcome_image = pygame.transform.smoothscale(self.player_with_sword_image, welcome_image_size)
        self.zombie_welcome_image = pygame.transform.smoothscale(self.zombie_image, welcome_image_size)

    def load_maze_algorithms(self):
        self.maze_algorithms = {}
        algorithm_dir = os.path.join(os.path.dirname(__file__), "mazeai")
        print(f"Searching for algorithms in directory: {algorithm_dir}")
        
        if not os.path.exists(algorithm_dir):
            print(f"Directory not found: {algorithm_dir}")
            return

        for filename in os.listdir(algorithm_dir):
            if filename.endswith('.js'):
                algorithm_name = filename[:-3].replace('-', '_')
                file_path = os.path.join(algorithm_dir, filename)
                try:
                    with open(file_path, 'r') as file:
                        js_code = file.read()
                    ctx = execjs.compile(js_code)
                    self.maze_algorithms[algorithm_name] = ctx
                    print(f"Loaded algorithm: {algorithm_name}")
                except Exception as e:
                    print(f"Error loading algorithm {algorithm_name}: {str(e)}")

        print(f"Loaded algorithms: {list(self.maze_algorithms.keys())}")

    def start_game(self):
        # Start a new game
        errors = self.validate_settings()
        if errors:
            print("Invalid settings:")
            for error in errors:
                print(error)
            return

        # Generate the maze
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                algorithm = self.settings["generation_algorithm"]
                print(f"Attempting to use algorithm: {algorithm}")
                maze_data = self.generate_maze(algorithm, self.settings["maze_width"], self.settings["maze_height"])
                if maze_data:
                    self.maze = Maze(self.settings["maze_height"], self.settings["maze_width"])
                    self.maze.grid = maze_data
                    if self.maze.find_solution():
                        print(f"Maze generated successfully on attempt {attempt + 1}")
                        break
                    else:
                        raise ValueError("Generated maze has no solution")
                else:
                    raise ValueError("Failed to generate maze")
            except Exception as e:
                print(f"Error generating maze (attempt {attempt + 1}): {str(e)}")
        else:
            print(f"Failed to generate a valid maze after {max_attempts} attempts. Using fallback method.")
            self.maze = Maze.generate_fallback(self.settings["maze_height"], self.settings["maze_width"])

        # Initialize game objects
        self.player = Player(self.maze.get_start_position())
        self.zombies = pygame.sprite.Group()
        self.swords = pygame.sprite.Group()

        # Place swords
        for _ in range(self.settings["sword_count"]):
            self.place_sword()

        # Reset game state
        self.score = 0
        self.game_over = False
        self.start_time = time.time()
        self.end_time = None

        # Set game state to playing
        self.state = "playing"

    def place_sword(self):
        x, y = self.get_random_empty_position()
        sword = pygame.sprite.Sprite()
        sword.image = self.sword_image
        sword.rect = sword.image.get_rect()
        sword.rect.center = (x, y)
        self.swords.add(sword)

    def get_random_empty_position(self):
        while True:
            x = random.randint(0, self.maze.width - 1)
            y = random.randint(0, self.maze.height - 1)
            if not self.maze.is_wall(x, y):
                return x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2

    def generate_maze(self, algorithm, width, height):
        if algorithm not in self.maze_algorithms:
            raise ValueError(f"Algorithm '{algorithm}' not found")
        
        ctx = self.maze_algorithms[algorithm]
        try:
            maze_data = ctx.call("generateMaze", width, height)
            return maze_data
        except Exception as e:
            print(f"Error generating maze with algorithm '{algorithm}': {str(e)}")
            return None

    def update_gameplay(self):
        if self.player is None:
            print("Player is None. Restarting game.")
            self.start_game()
            return True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.handle_player_movement(event.key)

        self.player.update()
        for zombie in self.zombies:
            zombie.update(1/30)  # Assuming 30 FPS

        self.check_collisions()
        self.spawn_zombies()
        self.update_score()

        if self.check_game_over():
            self.state = "game_over"
            self.end_time = time.time()

        self.draw()
        pygame.display.flip()

        return True

    def update_static_screen(self):
        # Update static screens (welcome, game over)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "welcome":
                    self.handle_welcome_click(event.pos)
                elif self.state == "game_over":
                    self.handle_game_over_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if self.state == "welcome":
                    self.handle_welcome_keydown(event)
                elif self.state == "game_over":
                    self.handle_game_over_keydown(event)
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.size)

        if self.state == "welcome":
            self.draw_welcome_screen()
        elif self.state == "game_over":
            self.draw_game_over_screen()

        pygame.display.flip()
        return True

    def draw(self):
        # Main drawing method
        self.screen.fill(BLACK)
        self.draw_maze()
        self.draw_player()
        self.draw_zombies()
        self.draw_sword()
        self.draw_legend()
        self.draw_score_board()

    def draw_welcome_screen(self):
        # Draw welcome screen
        self.screen.fill(BLACK)
        title = self.title_font.render("Escape the Zombies Maze", True, WHITE)
        instruction1 = self.font.render("Press SPACE to start", True, WHITE)
        instruction2 = self.font.render("Use arrow keys to move", True, WHITE)
        
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, self.screen_height // 4))
        self.screen.blit(instruction1, (self.screen_width // 2 - instruction1.get_width() // 2, self.screen_height // 2))
        self.screen.blit(instruction2, (self.screen_width // 2 - instruction2.get_width() // 2, self.screen_height // 2 + 50))

    def draw_maze(self):
        # Draw maze
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                if cell == 1:
                    pygame.draw.rect(self.screen, WHITE, rect)
                else:
                    pygame.draw.rect(self.screen, BLACK, rect)

    def draw_player(self):
        # Draw player
        self.screen.blit(self.player.image, self.player.rect)

    def draw_legend(self):
        # Draw game legend
        legend_items = [
            ("Player", ORANGE),
            ("Zombie", GREEN),
            ("Sword", YELLOW),
            ("Wall", WHITE)
        ]
        
        for i, (item, color) in enumerate(legend_items):
            text = self.font.render(item, True, color)
            self.screen.blit(text, (10, 10 + i * 30))

    def draw_score_board(self):
        # Draw score board
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (self.screen_width - score_text.get_width() - 10, 10))

    def validate_settings(self):
        errors = []
        if not (MIN_MAZE_WIDTH <= self.settings["maze_width"] <= MAX_MAZE_WIDTH):
            errors.append(f"Maze width must be between {MIN_MAZE_WIDTH} and {MAX_MAZE_WIDTH}.")
        if not (MIN_MAZE_HEIGHT <= self.settings["maze_height"] <= MAX_MAZE_HEIGHT):
            errors.append(f"Maze height must be between {MIN_MAZE_HEIGHT} and {MAX_MAZE_HEIGHT}.")
        if not (MIN_ZOMBIE_DELAY <= self.settings["zombie_delay"] <= MAX_ZOMBIE_DELAY):
            errors.append(f"Zombie delay must be between {MIN_ZOMBIE_DELAY} and {MAX_ZOMBIE_DELAY}.")
        if self.settings["generation_algorithm"] not in self.maze_algorithms:
            errors.append(f"Invalid maze generation algorithm: {self.settings['generation_algorithm']}")
        return errors

    def handle_welcome_click(self, pos):
        # Handle clicks on welcome screen
        # For simplicity, any click on the welcome screen starts the game
        self.state = "playing"
        self.start_time = time.time()

    def handle_welcome_keydown(self, event):
        # Handle key presses on welcome screen
        if event.key == pygame.K_SPACE:
            self.state = "playing"
            self.start_time = time.time()

    def replay_game(self):
        # Replay the game
        self.__init__(self.screen)
        self.state = "playing"
        self.start_time = time.time()

    def handle_resize(self, size):
        # Handle screen resize
        self.screen_width, self.screen_height = size
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        self.cell_size = min(self.screen_width // self.settings["maze_width"], self.screen_height // self.settings["maze_height"])
        self.calculate_maze_dimensions()

    def get_valid_moves(self):
        # Get valid moves for the player
        x, y = self.player.rect.center
        cell_x, cell_y = x // self.cell_size, y // self.cell_size
        valid_moves = []
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Up, Right, Down, Left
            new_x, new_y = cell_x + dx, cell_y + dy
            if 0 <= new_x < self.settings["maze_width"] and 0 <= new_y < self.settings["maze_height"] and self.maze[new_y][new_x] == 0:
                valid_moves.append((dx, dy))
        return valid_moves

    def update_valid_moves(self):
        # Update valid moves
        self.valid_moves = self.get_valid_moves()

    def move_zombies(self):
        # Move zombies
        for zombie in self.zombies:
            zombie.move(self.maze, self.cell_size)

    def handle_collision(self, zombie):
        # Handle collision between player and zombie
        if self.player.has_sword:
            self.zombies.remove(zombie)
            self.score += 10
            self.player.has_sword = False
            self.zombies_vanquished += 1
            print(f"Zombie vanquished! Total vanquished: {self.zombies_vanquished}")
        else:
            self.state = "game_over"
            self.end_time = time.time()

    def calculate_score(self):
        # Calculate player's score
        time_played = self.end_time - self.start_time
        return int(self.score + (1000 / time_played))

    def update_leaderboard(self, score):
        # Update the leaderboard
        self.leaderboard.append(score)
        self.leaderboard.sort(reverse=True)
        self.leaderboard = self.leaderboard[:10]  # Keep only top 10 scores

    def save_leaderboard(self):
        # Save the leaderboard to a file
        try:
            with open("leaderboard.json", "w") as f:
                json.dump(self.leaderboard, f)
        except IOError:
            print("Error saving leaderboard.")

    def calculate_maze_dimensions(self):
        # Calculate maze dimensions
        self.maze_top_left = ((self.screen_width - self.settings["maze_width"] * self.cell_size) // 2,
                              (self.screen_height - self.settings["maze_height"] * self.cell_size) // 2)

    def handle_keystroke(self, key):
        # Handle keystrokes during gameplay
        if key == pygame.K_UP and (0, -1) in self.valid_moves:
            self.player.rect.y -= self.cell_size
        elif key == pygame.K_RIGHT and (1, 0) in self.valid_moves:
            self.player.rect.x += self.cell_size
        elif key == pygame.K_DOWN and (0, 1) in self.valid_moves:
            self.player.rect.y += self.cell_size
        elif key == pygame.K_LEFT and (-1, 0) in self.valid_moves:
            self.player.rect.x -= self.cell_size

    def check_zombie_collisions(self):
        # Check for collisions between player and zombies
        for zombie in self.zombies:
            if self.player.rect.colliderect(zombie.rect):
                self.handle_collision(zombie)

    def handle_game_over_keydown(self, event):
        # Handle key presses on game over screen
        if event.key == pygame.K_SPACE:
            self.replay_game()
        elif event.key == pygame.K_ESCAPE:
            return False
        return True

    def update(self):
        # Main update method
        self.update_valid_moves()
        self.move_zombies()
        self.check_zombie_collisions()
        if self.sword and self.player.rect.colliderect(self.sword.rect):
            self.player.collect_sword()
            self.sword = None
        self.score += 1

    def draw_sword(self):
        self.swords.draw(self.screen)

# Additional helper methods as needed