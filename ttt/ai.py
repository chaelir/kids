import math
import random

def minimax(board, depth, alpha, beta, is_maximizing):
    winner = check_winner(board)
    if winner:
        return 100 if winner == 'Green' else -100 if winner == 'Red' else 0
    
    if depth == 0:
        return evaluate_board(board)
    
    if is_maximizing:
        best_score = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'Green'
                    score = minimax(board, depth - 1, alpha, beta, False)
                    board[i][j] = ' '
                    best_score = max(score, best_score)
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break
        return best_score
    else:
        best_score = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'Red'
                    score = minimax(board, depth - 1, alpha, beta, True)
                    board[i][j] = ' '
                    best_score = min(score, best_score)
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        break
        return best_score

def get_best_move(board):
    best_score = -math.inf
    best_move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'Green'
                score = minimax(board, 3, -math.inf, math.inf, False)
                board[i][j] = ' '
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
    return best_move

def get_available_moves(board):
    return [(i, j) for i in range(4) for j in range(4) if board[i][j] == ' ']

def evaluate_board(board):
    score = 0
    lines = (
        # Rows
        [board[i] for i in range(3)] +
        # Columns
        [[board[i][j] for i in range(3)] for j in range(3)] +
        # Diagonals
        [[board[i][i] for i in range(3)]] +
        [[board[i][2-i] for i in range(3)]]
    )
    
    for line in lines:
        score += evaluate_line(line)
    
    return score

def evaluate_line(line):
    line = list(line)  # Convert generator to list
    if line.count('Green') == 3:
        return 100
    elif line.count('Green') == 2 and line.count(' ') == 1:
        return 10
    elif line.count('Red') == 3:
        return -100
    elif line.count('Red') == 2 and line.count(' ') == 1:
        return -10
    return 0

def check_winner(board):
    # Check rows, columns, and diagonals
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != ' ':
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != ' ':
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]
    
    # Check for tie
    if all(board[i][j] != ' ' for i in range(3) for j in range(3)):
        return 'Tie'
    
    return None
