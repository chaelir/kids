import random
import execjs
from typing import Callable, List, Tuple

# Type aliases for clarity
Grid = List[List[int]]
Point = Tuple[int, int]

class Maze:
    def __init__(self, rows: int, cols: int, generation_algorithm: Callable[['Maze'], None]):
        # Ensure dimensions are odd
        self.rows = rows - 1 if rows % 2 == 0 else rows
        self.cols = cols - 1 if cols % 2 == 0 else cols
        self.grid: Grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        self.in_point: Point = (0, 1)
        self.out_point: Point = (self.rows - 1, self.cols - 2)
        self.solution: List[Point] = []
        self.generation_algorithm = generation_algorithm
        self.generate()

    def generate(self):
        print(f"Generating maze with size {self.rows}x{self.cols}")
        self.generation_algorithm(self)
        self.ensure_entrance_exit()
        self.solution = self.find_solution()
        print("Maze generation complete")
        print(self)

    def ensure_entrance_exit(self):
        self.grid[self.in_point[0]][self.in_point[1]] = 0
        self.grid[self.out_point[0]][self.out_point[1]] = 0

    def find_solution(self):
        def dfs(y: int, x: int, path: List[Point]) -> List[Point] | None:
            if (y, x) == self.out_point:
                return path
            for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.rows and 0 <= nx < self.cols and self.grid[ny][nx] == 0 and (ny, nx) not in path:
                    result = dfs(ny, nx, path + [(ny, nx)])
                    if result:
                        return result
            return None
        return dfs(self.in_point[0], self.in_point[1], [self.in_point]) or []

    def get_solution_length(self) -> int:
        return len(self.solution)

    def is_wall(self, row: int, col: int) -> bool:
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return True
        return self.grid[row][col] == 1

    def get_valid_neighbors(self, cell: Point) -> List[Point]:
        row, col = cell
        neighbors = []
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols and not self.is_wall(new_row, new_col):
                neighbors.append((new_row, new_col))
        return neighbors

    def __str__(self) -> str:
        maze_str = ""
        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) == self.in_point:
                    maze_str += "S "
                elif (row, col) == self.out_point:
                    maze_str += "E "
                elif self.grid[row][col] == 1:
                    maze_str += "# "
                else:
                    maze_str += ". "
            maze_str += "\n"
        return maze_str

    def add_outer_walls(self):
        for i in range(self.rows):
            self.grid[i][0] = self.grid[i][self.cols-1] = 1
        for j in range(self.cols):
            self.grid[0][j] = self.grid[self.rows-1][j] = 1

# Maze generation algorithms

def recursive_division(maze: Maze):
    # Make dimensions odd
    maze.cols -= maze.cols % 2
    maze.cols += 1
    maze.rows -= maze.rows % 2
    maze.rows += 1

    def divide(i_coords, j_coords, hv):
        i_dim = i_coords[1] - i_coords[0]
        j_dim = j_coords[1] - j_coords[0]

        if i_dim <= 0 or j_dim <= 0:
            return

        if hv == "h":
            split = random.randrange(i_coords[0], i_coords[1] + 1, 2)
            hole = random.randrange(j_coords[0] + 1, j_coords[1] + 1, 2)

            for j in range(j_coords[0], j_coords[1] + 1):
                if j != hole:
                    maze.grid[split][j] = 1

            divide([i_coords[0], split - 1], j_coords, horv(split - i_coords[0] - 1, j_dim))
            divide([split + 1, i_coords[1]], j_coords, horv(i_coords[1] - split - 1, j_dim))

        else:
            split = random.randrange(j_coords[0], j_coords[1] + 1, 2)
            hole = random.randrange(i_coords[0] + 1, i_coords[1] + 1, 2)

            for i in range(i_coords[0], i_coords[1] + 1):
                if i != hole:
                    maze.grid[i][split] = 1

            divide(i_coords, [j_coords[0], split - 1], horv(i_dim, split - j_coords[0] - 1))
            divide(i_coords, [split + 1, j_coords[1]], horv(i_dim, j_coords[1] - split - 1))

    def horv(i_dim, j_dim):
        if i_dim < j_dim:
            return "v"
        elif j_dim < i_dim:
            return "h"
        else:
            return random.choice(["h", "v"])

    # Initialize the grid with passages
    maze.grid = [[0 for _ in range(maze.cols)] for _ in range(maze.rows)]

    # Add outer walls
    for i in range(maze.rows):
        maze.grid[i][0] = maze.grid[i][maze.cols - 1] = 1
    for j in range(maze.cols):
        maze.grid[0][j] = maze.grid[maze.rows - 1][j] = 1

    # Start the recursive division
    divide([1, maze.rows - 2], [1, maze.cols - 2], horv(maze.rows - 2, maze.cols - 2))

    # Ensure entrance and exit
    maze.grid[0][1] = 0
    maze.grid[maze.rows - 1][maze.cols - 2] = 0

def backtracking(maze: Maze):
    try:
        # Read the JavaScript code from the file
        with open('backtracking.js', 'r') as file:
            js_code = file.read()

        # Create a JavaScript context
        ctx = execjs.compile(js_code)

        # Call the JavaScript function
        js_maze = ctx.call("backtrackingMaze", maze.cols, maze.rows)

        # Print the JavaScript-generated maze
        print("JavaScript-generated maze:")
        for row in js_maze:
            print(''.join(['#' if cell == 1 else ' ' for cell in row]))
        print()  # Add an empty line after the maze

        # Convert the JavaScript maze to Python and update the Maze object
        maze.grid = js_maze

    except Exception as e:
        print(f"Error in backtracking maze generation: {e}")
        print("Falling back to a simple maze...")
        # Create a simple maze as a fallback
        maze.grid = [[1 for _ in range(maze.cols)] for _ in range(maze.rows)]
        for i in range(1, maze.rows - 1, 2):
            for j in range(1, maze.cols - 1, 2):
                maze.grid[i][j] = 0

    # Ensure entrance and exit are open
    maze.grid[maze.in_point[0]][maze.in_point[1]] = 0
    maze.grid[maze.out_point[0]][maze.out_point[1]] = 0

# Generic test function
def test_maze_generation(algorithm: Callable[[Maze], None], algorithm_name: str, num_tests: int = 1):
    print(f"Running {num_tests} tests for {algorithm_name} algorithm...")
    
    last_maze = None
    
    for i in range(num_tests):
        rows = 11  # Odd number
        cols = 11  # Odd number
        
        maze = Maze(rows, cols, algorithm)
        last_maze = maze
        
        print(f"\nGenerated maze (Test {i+1}):")
        print(maze)  # Print the maze after generation

        # Check if entrance and exit are open
        if maze.grid[maze.in_point[0]][maze.in_point[1]] != 0 or maze.grid[maze.out_point[0]][maze.out_point[1]] != 0:
            print(f"Test {i+1} failed: Entrance or exit is blocked")
            return False
        
        # Check if there's a valid path from entrance to exit
        if not maze.solution:
            print(f"Test {i+1} failed: No valid path from entrance to exit")
            return False
        
        print(f"Test {i+1} passed: Maze size {rows}x{cols}")
    
    print(f"All tests passed successfully for {algorithm_name}!")
    
    if last_maze:
        print(f"\nLast generated maze using {algorithm_name}:")
        print(last_maze)
    
    return True

if __name__ == "__main__":
    #test_maze_generation(recursive_division, "Recursive Division")
    test_maze_generation(backtracking, "Backtracking")