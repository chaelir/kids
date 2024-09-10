import random

def get_best_move(board):
    print("AI is thinking...")
    print("Current board state:")
    for row in board:
        print(row)
    
    available_moves = []
    for i in range(4):
        for j in range(4):
            if board[i][j] == ' ':
                available_moves.append((i, j))
    
    if not available_moves:
        return None
    
    best_move = random.choice(available_moves)
    print(f"AI chose move: {best_move}")
    return best_move

def check_winner(board):
    # Check rows and columns
    for i in range(4):
        if board[i][0] == board[i][1] == board[i][2] == board[i][3] != ' ':
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] == board[3][i] != ' ':
            return board[0][i]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] == board[3][3] != ' ':
        return board[0][0]
    if board[0][3] == board[1][2] == board[2][1] == board[3][0] != ' ':
        return board[0][3]
    
    return None

def is_full(board):
    return all(cell != ' ' for row in board for cell in row)