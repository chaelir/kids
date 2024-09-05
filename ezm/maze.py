import random
from ezm.constants import MAZE_WIDTH, MAZE_HEIGHT

class Maze:
    def __init__(self, maze_data=None):
        if maze_data:
            self.grid = maze_data
            self.height = len(maze_data)
            self.width = len(maze_data[0]) if self.height > 0 else 0
        else:
            self.width = MAZE_WIDTH
            self.height = MAZE_HEIGHT
            self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
            self.generate()

    def generate(self):
        # Existing generation method
        for y in range(1, self.height - 1, 2):
            for x in range(1, self.width - 1, 2):
                self.grid[y][x] = 0
                if x < self.width - 2:
                    self.grid[y][x + 1] = 0
                if y < self.height - 2:
                    self.grid[y + 1][x] = 0

    @classmethod
    def generate_fallback(cls, height, width):
        maze = cls()
        maze.width = width
        maze.height = height
        maze.grid = [[1 for _ in range(width)] for _ in range(height)]
        maze.generate()
        return maze

    def is_wall(self, x, y):
        return self.grid[y][x] == 1

    def get_start_position(self):
        # Find the first open cell in the top row
        for x in range(self.width):
            if not self.is_wall(x, 0):
                return x, 0
        # If no open cell found, return the top-left corner
        return 0, 0

    def has_solution(self):
        # Implement a simple check to see if there's a path from start to end
        # This is a placeholder and should be replaced with a proper pathfinding algorithm
        return True

    # Add other maze-related methods as needed