import random
from sudoku_board import SudokuBoard
from game_manager import Difficulty

class SudokuSolver:
    def generate_puzzle(self, difficulty):
        board = SudokuBoard()
        self.fill_board(board)
        self.remove_numbers(board, difficulty)
        return board
    
    def fill_board(self, board):
        self.solve_puzzle(board)
    
    def remove_numbers(self, board, difficulty):
        cells_to_remove = {
            Difficulty.EASY: 40,
            Difficulty.MEDIUM: 50,
            Difficulty.HARD: 60,
            Difficulty.EXPERT: 70
        }[difficulty]
        
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        for i, j in cells[:cells_to_remove]:
            board.set_cell(i, j, 0)
    
    def solve_puzzle(self, board):
        empty = board.get_empty_cell()
        if not empty:
            return True
        row, col = empty
        
        nums = list(range(1, 10))
        random.shuffle(nums)
        for num in nums:
            if self.is_safe(board, row, col, num):
                board.set_cell(row, col, num)
                if self.solve_puzzle(board):
                    return True
                board.set_cell(row, col, 0)
        
        return False
    
    def is_safe(self, board, row, col, num):
        # Check row
        if num in [board.get_cell(row, i) for i in range(9) if board.get_cell(row, i) != 0]:
            return False
        
        # Check column
        if num in [board.get_cell(i, col) for i in range(9) if board.get_cell(i, col) != 0]:
            return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board.get_cell(i, j) == num:
                    return False
        
        return True
    
    def get_hint(self, board):
        solved_board = board.copy()
        if self.solve_puzzle(solved_board):
            for i in range(9):
                for j in range(9):
                    if board.get_cell(i, j) == 0:
                        return i, j, solved_board.get_cell(i, j)
        return None