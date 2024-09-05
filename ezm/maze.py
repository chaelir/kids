import random
from ezm.constants import MAZE_WIDTH, MAZE_HEIGHT

class Maze:
    def __init__(self):
        self.width = MAZE_WIDTH
        self.height = MAZE_HEIGHT
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        self.generate()

    def generate(self):
        # Implement maze generation algorithm here
        # This is a placeholder for a simple random maze
        for y in range(1, self.height - 1, 2):
            for x in range(1, self.width - 1, 2):
                self.grid[y][x] = 0
                if x < self.width - 2:
                    self.grid[y][x + 1] = 0
                if y < self.height - 2:
                    self.grid[y + 1][x] = 0

    def is_wall(self, x, y):
        return self.grid[y][x] == 1

    # Add other maze-related methods as needed