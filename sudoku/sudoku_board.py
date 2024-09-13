class SudokuBoard:
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
    
    def set_cell(self, row, col, value):
        self.board[row][col] = value
    
    def get_cell(self, row, col):
        return self.board[row][col]
    
    def is_valid(self):
        for i in range(9):
            if not (self.is_row_valid(i) and self.is_column_valid(i) and self.is_box_valid(i)):
                return False
        return True
    
    def is_row_valid(self, row):
        return len(set(self.board[row]) - {0}) == len([x for x in self.board[row] if x != 0])
    
    def is_column_valid(self, col):
        column = [self.board[i][col] for i in range(9)]
        return len(set(column) - {0}) == len([x for x in column if x != 0])
    
    def is_box_valid(self, box):
        row, col = (box // 3) * 3, (box % 3) * 3
        box_values = [self.board[i][j] for i in range(row, row + 3) for j in range(col, col + 3)]
        return len(set(box_values) - {0}) == len([x for x in box_values if x != 0])
    
    def is_complete(self):
        return all(all(cell != 0 for cell in row) for row in self.board)
    
    def get_empty_cell(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return i, j
        return None
    
    def copy(self):
        new_board = SudokuBoard()
        for i in range(9):
            for j in range(9):
                new_board.set_cell(i, j, self.get_cell(i, j))
        return new_board