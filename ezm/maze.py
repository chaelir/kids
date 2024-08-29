import random
import execjs
import os
from typing import List, Tuple

# Type aliases for clarity
Grid = List[List[int]]
Point = Tuple[int, int]

class Maze:
    def __init__(self, rows: int, cols: int, generation_algorithm: str = 'recursive_division'):
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
        print(f"Generating maze with size {self.rows}x{self.cols} using {self.generation_algorithm} algorithm")
        js_file = f'{self.generation_algorithm.replace("_", "-")}.js'
        
        algorithms = {
            'backtracking': 'backtrackingMaze',
            'hunt_and_kill': 'huntAndKillMaze',
            'wilsons': 'wilsonsMaze',
            'ellers': 'ellersMaze',
            'kruskals': 'kruskalsMaze',
            'aldous_broder': 'aldousBroderMaze',
            'sidewinder': 'sidewinderMaze',
            'binary_tree': 'binaryTreeMaze',
            'prims': 'primsMaze',
            'recursive_division': 'recursiveDivisionMaze'
        }
        
        if self.generation_algorithm not in algorithms:
            print(f"Unknown algorithm: {self.generation_algorithm}. Using backtracking.")
            self.generation_algorithm = 'backtracking'
        
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            js_file_path = os.path.join(script_dir, 'mazeai', js_file)
            
            with open(js_file_path, 'r') as file:
                js_code = file.read()

            ctx = execjs.compile(js_code)
            js_maze = ctx.call(algorithms[self.generation_algorithm], self.cols, self.rows)

            print(f"JavaScript-generated maze using {self.generation_algorithm}:")
            for row in js_maze:
                print(''.join(['#' if cell == 1 else ' ' for cell in row]))
            print()  # Add an empty line after the maze

            self.grid = js_maze
        except Exception as e:
            print(f"Error in {self.generation_algorithm} maze generation: {e}")
            print("Falling back to a simple maze...")
            self.create_simple_maze()

        self.ensure_entrance_exit()
        self.solution = self.find_solution()
        print("Maze generation complete")
        print(self)

    def create_simple_maze(self):
        self.grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        for i in range(1, self.rows - 1, 2):
            for j in range(1, self.cols - 1, 2):
                self.grid[i][j] = 0

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

# Update the test_maze_generation function
def test_maze_generation(num_tests: int = 1):
    algorithms = [
        'recursive_division', 'backtracking', 'hunt_and_kill', 'wilsons',
        'ellers', 'kruskals', 'aldous_broder', 'sidewinder', 'binary_tree', 'prims'
    ]
    
    for algorithm in algorithms:
        print(f"\nRunning {num_tests} tests for {algorithm} algorithm...")
        
        for i in range(num_tests):
            rows = 11  # Odd number
            cols = 11  # Odd number
            
            maze = Maze(rows, cols, algorithm)
            
            print(f"\nGenerated maze (Test {i+1}):")
            print(maze)

            if maze.grid[maze.in_point[0]][maze.in_point[1]] != 0 or maze.grid[maze.out_point[0]][maze.out_point[1]] != 0:
                print(f"Test {i+1} failed: Entrance or exit is blocked")
                return False
            
            if not maze.solution:
                print(f"Test {i+1} failed: No valid path from entrance to exit")
                return False
            
            print(f"Test {i+1} passed: Maze size {rows}x{cols}")
        
        print(f"All tests passed successfully for {algorithm}!")
    
    return True

if __name__ == "__main__":
    test_maze_generation()