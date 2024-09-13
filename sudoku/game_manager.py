import time
from enum import Enum
from sudoku_board import SudokuBoard

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4

class GameManager:
    def __init__(self, solver):
        self.solver = solver
        self.board = None
        self.difficulty = Difficulty.EASY
        self.start_time = None
        self.elapsed_time = 0
        self.score = 0
        self.move_history = []
    
    def new_game(self):
        try:
            self.board = self.solver.generate_puzzle(self.difficulty)
            self.start_time = time.time()
            self.elapsed_time = 0
            self.score = 0
            self.move_history.clear()
        except Exception as e:
            print(f"Error generating new game: {e}")
            self.board = SudokuBoard()  # Create an empty board as fallback
    
    def undo(self):
        if self.move_history:
            row, col, prev_value = self.move_history.pop()
            self.board.set_cell(row, col, prev_value)
    
    def hint(self):
        hint = self.solver.get_hint(self.board)
        if hint:
            row, col, value = hint
            self.board.set_cell(row, col, value)
    
    def check(self):
        return self.board.is_valid()
    
    def solve(self):
        self.solver.solve_puzzle(self.board)
    
    def update_time(self):
        if self.start_time:
            self.elapsed_time = int(time.time() - self.start_time)
    
    def make_move(self, row, col, value):
        if self.board.get_cell(row, col) == 0:
            prev_value = self.board.get_cell(row, col)
            self.board.set_cell(row, col, value)
            self.move_history.append((row, col, prev_value))
            
            if self.board.is_complete() and self.board.is_valid():
                self.calculate_score()
    
    def calculate_score(self):
        base_score = {
            Difficulty.EASY: 1000,
            Difficulty.MEDIUM: 2000,
            Difficulty.HARD: 3000,
            Difficulty.EXPERT: 4000
        }[self.difficulty]
        time_penalty = self.elapsed_time // 60  # Penalty for each minute
        self.score = max(0, base_score - time_penalty)