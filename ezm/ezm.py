import pygame
import time
import json
from maze import Maze, backtracking

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
WHITE, BLACK, RED, GREEN, BLUE, MAGENTA, YELLOW, LIGHT_GRAY, ORANGE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255), (255, 255, 0), (200, 200, 200), (255, 165, 0)
MIN_MAZE_HEIGHT, MAX_MAZE_HEIGHT = 9, 99
MIN_MAZE_WIDTH, MAX_MAZE_WIDTH = 9, 99
MIN_ZOMBIE_DELAY, MAX_ZOMBIE_DELAY = 5, 10

class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.margin = 20
        self.legend_width = 200
        self.maze_area_width = self.screen_width - self.legend_width - 3 * self.margin
        self.maze_area_height = self.screen_height - 2 * self.margin
        self.offset_x = self.margin
        self.offset_y = self.margin
        self.cell_size = None

        self.leaderboard = self.load_leaderboard()
        self.maze = None
        self.player_position = None
        self.zombie_flood = set()
        self.player_path = []
        self.tentative_path = []
        self.valid_moves = set()
        self.game_finished = False
        self.game_message = ""
        self.zombie_flood_start_time = None

        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)

        self.ZOMBIE_UPDATE_EVENT = pygame.USEREVENT + 1

        self.state = "welcome"
        self.settings = {
            "maze_width": 9,
            "maze_height": 9,
            "zombie_delay": 5,
            "zombie_speed_fast": True,  # Default to True
            "zombie_flooding_enabled": True  # Default to True
        }
        self.player_name = ""
        self.input_boxes = {
            "player_name": pygame.Rect(0, 0, 200, 32),
            "maze_width": pygame.Rect(0, 0, 60, 32),
            "maze_height": pygame.Rect(0, 0, 60, 32),
            "zombie_delay": pygame.Rect(0, 0, 60, 32)
        }
        self.active_input = None

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        self.maze_generation_algorithm = backtracking
        self.cursor_size = 3

        self.cursor = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.cursor, (255, 0, 0, 128), (7, 7), 7)
        pygame.mouse.set_visible(False)

        self.last_move_time = 0
        self.move_delay = 0.1  # 200 milliseconds delay between moves

    # Game initialization and state management
    def start_game(self):
        if not self.validate_settings():
            return
        
        max_attempts = 5
        for _ in range(max_attempts):
            self.maze = Maze(self.settings["maze_height"], self.settings["maze_width"], self.maze_generation_algorithm)
            if self.maze.solution:
                break
        else:
            print(f"Failed to generate a valid maze after {max_attempts} attempts. Please try again.")
            self.state = "welcome"
            return

        self.player_position = self.maze.in_point
        self.zombie_flood = set()
        self.player_path = []
        self.tentative_path = []
        self.game_finished = False
        self.game_message = ""
        self.state = "playing"
        self.zombie_flood_start_time = time.time() + self.settings["zombie_delay"]

        self.cell_size = min(self.maze_area_width // self.maze.cols, self.maze_area_height // self.maze.rows)
        self.offset_x = self.margin + (self.maze_area_width - self.cell_size * self.maze.cols) // 2
        self.offset_y = self.margin + (self.maze_area_height - self.cell_size * self.maze.rows) // 2

        self.update_zombie_timer()
        self.update_valid_moves()

    def update_zombie_timer(self):
        interval = int(self.settings["zombie_delay"] * 1000 * (0.5 if self.settings["zombie_speed_fast"] else 1))
        pygame.time.set_timer(self.ZOMBIE_UPDATE_EVENT, interval)

    def game_over(self, message):
        self.state = "game_over"
        self.game_message = message

    # Drawing methods
    def draw(self):
        self.screen.fill(WHITE)
        
        if self.state == "welcome":
            self.draw_welcome_screen()
        elif self.state == "playing":
            self.draw_maze()
            self.draw_player()
            self.draw_legend()  # Only draw the legend during gameplay
        elif self.state == "game_over":
            self.draw_score_board()

        # Draw custom cursor
        mouse_pos = pygame.mouse.get_pos()
        self.screen.blit(self.cursor, (mouse_pos[0] - 7, mouse_pos[1] - 7))
        
        pygame.display.flip()

    def draw_welcome_screen(self):
        self.screen.fill(BLACK)

        title = self.title_font.render("Welcome to EscapeZombMania!", True, RED)  # Changed to RED
        title_rect = title.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title, title_rect)

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
            "2. Avoid zombies that flood the maze.",
            "3. Use arrow keys or click to move.",
            "4. Zombies move at regular intervals.",
            "5. Game ends when you reach the exit or",
            "   get caught by zombies.",
            "6. Score based on maze size, zombie speed,",
            "   and time taken (if flooding enabled)."
        ]

        for i, rule in enumerate(rules):
            rule_surface = self.font.render(rule, True, WHITE)
            self.screen.blit(rule_surface, (rules_pane.x + 10, rules_pane.y + 50 + i * 30))

        # Game Controls
        controls_title = self.title_font.render("Game Controls", True, WHITE)
        self.screen.blit(controls_title, (controls_pane.x + 10, controls_pane.y + 10))

        y = controls_pane.y + 50
        for setting in ["player_name", "maze_width", "maze_height", "zombie_delay"]:
            text = f"{setting.replace('_', ' ').title()}: "
            setting_surface = self.font.render(text, True, WHITE)
            self.screen.blit(setting_surface, (controls_pane.x + 10, y))
            
            input_box = self.input_boxes[setting]
            input_box.topleft = (controls_pane.x + 180, y - 5)  # Adjusted y position
            pygame.draw.rect(self.screen, WHITE if self.active_input == setting else LIGHT_GRAY, input_box, 2)
            value = self.player_name if setting == "player_name" else str(self.settings[setting])
            value_surface = self.font.render(value, True, WHITE)
            self.screen.blit(value_surface, (input_box.x + 5, input_box.y + 5))
            
            if setting == "zombie_delay":
                unit_surface = self.font.render("s", True, WHITE)
                self.screen.blit(unit_surface, (input_box.right + 5, input_box.y + 5))
                range_text = "(5-10)"
                range_surface = self.font.render(range_text, True, LIGHT_GRAY)
                self.screen.blit(range_surface, (input_box.right + 25, input_box.y + 5))
            elif setting != "player_name":
                range_text = "(9-99)" if setting == "maze_width" else "(9-99)"
                range_surface = self.font.render(range_text, True, LIGHT_GRAY)
                self.screen.blit(range_surface, (input_box.right + 10, input_box.y + 5))
            
            y += 50

        speed_text = f"Zombie Speed: {'Fast' if self.settings['zombie_speed_fast'] else 'Slow'}"
        speed_surface = self.font.render(speed_text, True, WHITE)
        self.screen.blit(speed_surface, (controls_pane.x + 10, y))
        speed_toggle = self.font.render("Press S to toggle", True, LIGHT_GRAY)
        self.screen.blit(speed_toggle, (controls_pane.x + 10, y + 30))

        y += 70
        flood_text = f"Zombie Flooding: {'ON' if self.settings['zombie_flooding_enabled'] else 'OFF'}"
        flood_surface = self.font.render(flood_text, True, WHITE)
        self.screen.blit(flood_surface, (controls_pane.x + 10, y))
        flood_toggle = self.font.render("Press F to toggle", True, LIGHT_GRAY)
        self.screen.blit(flood_toggle, (controls_pane.x + 10, y + 30))

        start_text = self.font.render("Press Enter to Start Game or ESC to Quit", True, WHITE)
        start_text_rect = start_text.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
        self.screen.blit(start_text, start_text_rect)

    def draw_legend(self):
        legend_x = self.screen_width - self.legend_width - self.margin
        legend_y = self.margin
        legend_height = self.screen_height - 2 * self.margin

        pygame.draw.rect(self.screen, WHITE, (legend_x, legend_y, self.legend_width, legend_height))
        pygame.draw.rect(self.screen, BLACK, (legend_x, legend_y, self.legend_width, legend_height), 2)

        title_surface = self.title_font.render("Map Guide", True, BLACK)
        title_rect = title_surface.get_rect(center=(legend_x + self.legend_width // 2, legend_y + 25))
        self.screen.blit(title_surface, title_rect)

        legend_items = [
            ("Player", MAGENTA),
            ("Walls", BLACK),
            ("Zombies", RED),
            ("IN", GREEN),
            ("OUT", BLUE),
            ("Hint", ORANGE)
        ]
        for i, (text, color) in enumerate(legend_items):
            pygame.draw.rect(self.screen, color, (legend_x + 10, legend_y + 60 + i*30, 20, 20))
            text_surface = self.font.render(text, True, color)
            self.screen.blit(text_surface, (legend_x + 40, legend_y + 60 + i*30))

        if self.state == "playing":
            info_text = [
                f"Maze Size: {self.maze.rows}x{self.maze.cols}",
                f"Solution Length: {self.maze.get_solution_length()}",
                f"Zombie Delay: {self.settings['zombie_delay']}s",
                f"Zombie Speed: {'Fast' if self.settings['zombie_speed_fast'] else 'Slow'}",
                f"Flooding: {'ON' if self.settings['zombie_flooding_enabled'] else 'OFF'}"
            ]
            for i, text in enumerate(info_text):
                info_surface = self.font.render(text, True, BLACK)
                self.screen.blit(info_surface, (legend_x + 10, legend_y + 240 + i * 30))

    def draw_maze(self):
        pygame.draw.rect(self.screen, BLACK, (self.offset_x, self.offset_y, 
                                              self.cell_size * self.maze.cols, self.cell_size * self.maze.rows), 2)

        for row in range(self.maze.rows):
            for col in range(self.maze.cols):
                x = self.offset_x + col * self.cell_size
                y = self.offset_y + row * self.cell_size
                if self.maze.is_wall(row, col):
                    pygame.draw.rect(self.screen, BLACK, (x, y, self.cell_size, self.cell_size))
                if (row, col) in self.zombie_flood:
                    pygame.draw.rect(self.screen, RED, (x, y, self.cell_size, self.cell_size))

        pygame.draw.rect(self.screen, GREEN, (self.offset_x + self.maze.in_point[1] * self.cell_size,
                                              self.offset_y + self.maze.in_point[0] * self.cell_size,
                                              self.cell_size, self.cell_size))
        pygame.draw.rect(self.screen, BLUE, (self.offset_x + self.maze.out_point[1] * self.cell_size,
                                             self.offset_y + self.maze.out_point[0] * self.cell_size,
                                             self.cell_size, self.cell_size))

    def draw_player(self):
        # Draw the player path
        if len(self.player_path) > 1:
            pygame.draw.lines(self.screen, MAGENTA, False, 
                              [(self.offset_x + col * self.cell_size + self.cell_size // 2, 
                                self.offset_y + row * self.cell_size + self.cell_size // 2) 
                               for row, col in self.player_path], 
                              width=3)

        # Draw tentative path
        if len(self.tentative_path) > 1:
            pygame.draw.lines(self.screen, YELLOW, False, 
                              [(self.offset_x + col * self.cell_size + self.cell_size // 2, 
                                self.offset_y + row * self.cell_size + self.cell_size // 2) 
                               for row, col in self.tentative_path], 
                              width=2)

        # Draw current player position
        player_x = self.offset_x + self.player_position[1] * self.cell_size + self.cell_size // 2
        player_y = self.offset_y + self.player_position[0] * self.cell_size + self.cell_size // 2
        pygame.draw.circle(self.screen, MAGENTA, (player_x, player_y), self.cell_size // 3)

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

    # Event handling methods
    def handle_welcome_click(self, pos):
        for setting, box in self.input_boxes.items():
            if box.collidepoint(pos):
                self.active_input = setting
                return
        self.active_input = None

    def handle_welcome_keydown(self, event):
        if self.active_input:
            if event.key == pygame.K_RETURN:
                self.active_input = None
            elif event.key == pygame.K_BACKSPACE:
                if self.active_input == "player_name":
                    self.player_name = self.player_name[:-1]
                else:
                    self.settings[self.active_input] = int(str(self.settings[self.active_input])[:-1] or "0")
            elif self.active_input == "player_name":
                self.player_name += event.unicode
            elif event.unicode.isdigit():
                if self.active_input in ["maze_width", "maze_height", "zombie_delay"]:
                    current_value = str(self.settings[self.active_input])
                    new_value = int(current_value + event.unicode)
                    self.settings[self.active_input] = new_value
        elif event.key == pygame.K_s:
            self.settings["zombie_speed_fast"] = not self.settings["zombie_speed_fast"]
        elif event.key == pygame.K_f:
            self.settings["zombie_flooding_enabled"] = not self.settings["zombie_flooding_enabled"]
        elif event.key == pygame.K_RETURN:
            if self.validate_settings():
                self.start_game()
            else:
                print("Please ensure all settings are valid before starting the game.")
        self.draw_welcome_screen()

    def handle_maze_click(self, pos):
        cell = self.get_cell_from_pos(pos)
        if cell and cell in self.valid_moves:
            self.tentative_path = self.get_path_to_cell(cell)

    def handle_maze_hover(self, pos):
        cell = self.get_cell_from_pos(pos)
        if cell and cell in self.valid_moves:
            self.tentative_path = self.get_path_to_cell(cell)
        else:
            self.tentative_path = []

    def handle_game_over_keydown(self, event):
        if event.key == pygame.K_RETURN:
            self.replay_game()
        elif event.key == pygame.K_ESCAPE:
            self.state = "welcome"
            self.draw_welcome_screen()
        return True

    def replay_game(self):
        # Reset game state
        self.player_position = None
        self.zombie_flood = set()
        self.player_path = []
        self.tentative_path = []
        self.game_finished = False
        self.game_message = ""
        
        # Start a new game with the same settings
        self.start_game()

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

    def update_zombie_flood(self):
        if not self.settings["zombie_flooding_enabled"] or time.time() < self.zombie_flood_start_time:
            return
        if not self.zombie_flood:
            self.zombie_flood.add(self.maze.in_point)
            return

        new_cells = set()
        for cell in self.zombie_flood:
            for neighbor in self.maze.get_valid_neighbors(cell):
                if neighbor not in self.zombie_flood and not self.maze.is_wall(*neighbor):
                    new_cells.add(neighbor)
        
        self.zombie_flood.update(new_cells)
        self.update_valid_moves()

    def calculate_score(self):
        if not self.settings["zombie_flooding_enabled"]:
            return 0
        
        maze_difficulty = self.maze.rows * self.maze.cols
        zombie_time_factor = 10 / self.settings["zombie_delay"]
        speed_factor = 2 if self.settings["zombie_speed_fast"] else 1
        return int(maze_difficulty * zombie_time_factor * speed_factor)

    def validate_settings(self):
        if not self.player_name.strip():
            print("Please enter a player name.")
            return False
        if not (MIN_MAZE_WIDTH <= self.settings["maze_width"] <= MAX_MAZE_WIDTH):
            print(f"Maze width must be between {MIN_MAZE_WIDTH} and {MAX_MAZE_WIDTH}.")
            return False
        if not (MIN_MAZE_HEIGHT <= self.settings["maze_height"] <= MAX_MAZE_HEIGHT):
            print(f"Maze height must be between {MIN_MAZE_HEIGHT} and {MAX_MAZE_HEIGHT}.")
            return False
        if not (MIN_ZOMBIE_DELAY <= self.settings["zombie_delay"] <= MAX_ZOMBIE_DELAY):
            print(f"Zombie delay must be between {MIN_ZOMBIE_DELAY} and {MAX_ZOMBIE_DELAY}.")
            return False
        return True

    # Leaderboard methods
    def update_leaderboard(self, score):
        self.leaderboard.append((self.player_name, score))
        self.leaderboard.sort(key=lambda x: x[1], reverse=True)
        self.leaderboard = self.leaderboard[:10]
        self.save_leaderboard()

    def load_leaderboard(self):
        try:
            with open('leaderboard.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_leaderboard(self):
        try:
            with open('leaderboard.json', 'w') as f:
                json.dump(self.leaderboard, f)
        except IOError:
            print("Error saving leaderboard.")

    # Main game loop
    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "welcome":
                        self.handle_welcome_click(event.pos)
                    elif self.state == "playing":
                        self.handle_maze_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    if self.state == "playing":
                        self.handle_maze_hover(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing" or self.state == "game_over":
                            self.state = "welcome"
                            self.draw_welcome_screen()
                        else:
                            running = False
                    elif self.state == "welcome":
                        self.handle_welcome_keydown(event)
                    elif self.state == "game_over":
                        self.handle_game_over_keydown(event)
                    elif self.state == "playing":
                        self.handle_keystroke(event.key)
                elif event.type == self.ZOMBIE_UPDATE_EVENT and self.state == "playing":
                    if self.settings["zombie_flooding_enabled"]:
                        self.update_zombie_flood()
                        self.update_valid_moves()

            # Handle held keys for continuous movement
            keys = pygame.key.get_pressed()
            if self.state == "playing":
                for key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    if keys[key]:
                        self.handle_keystroke(key)

            if self.state == "playing":
                if self.player_position in self.zombie_flood:
                    self.game_over("Game Over! You've been caught by zombies.")
                elif self.player_position == self.maze.out_point:
                    score = self.calculate_score()
                    self.game_over(f"You win! Score: {score}")
                    self.update_leaderboard(score)

            self.draw()
            clock.tick(60)
        return False

    def handle_keystroke(self, key):
        if self.state != "playing":
            return

        current_time = time.time()
        if current_time - self.last_move_time < self.move_delay:
            return  # Ignore keystroke if not enough time has passed

        move = {
            pygame.K_UP: (-1, 0),
            pygame.K_DOWN: (1, 0),
            pygame.K_LEFT: (0, -1),
            pygame.K_RIGHT: (0, 1)
        }.get(key)

        if move:
            current_row, current_col = self.player_position
            new_row = current_row + move[0]
            new_col = current_col + move[1]
            new_pos = (new_row, new_col)
            
            # Check if the new position is valid
            if new_pos in self.valid_moves:
                # Check if the new position is in the tentative path
                if not self.tentative_path or new_pos in self.tentative_path:
                    self.player_position = new_pos
                    self.player_path.append(new_pos)
                    
                    # Update tentative path
                    if self.tentative_path:
                        # Remove all cells up to and including the new position
                        while self.tentative_path and self.tentative_path[0] != new_pos:
                            self.tentative_path.pop(0)
                        if self.tentative_path:
                            self.tentative_path.pop(0)  # Remove the new position itself
                    
                    self.update_valid_moves()
                    self.last_move_time = current_time  # Update the last move time

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("EscapeZombMania!")

    game = Game(screen)
    game.run()

    pygame.quit()

if __name__ == "__main__":
    main()
