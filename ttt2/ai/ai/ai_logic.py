import random

def get_best_move(board):
    best_score = float('-inf')
    best_move = None
    for i in range(5):
        for j in range(5):
            if board[i][j] == ' ':
                board[i][j] = 'Green'
                score = minimax(board, 0, False)
                board[i][j] = ' '
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
    return best_move

def minimax(board, depth, is_maximizing):
    winner = check_winner(board)
    if winner == 'Green':
        return 1
    elif winner == 'Red':
        return -1
    elif is_board_full(board):
        return 0

    if is_maximizing:
        best_score = float('-inf')
        for i in range(5):
            for j in range(5):
                if board[i][j] == ' ':
                    board[i][j] = 'Green'
                    score = minimax(board, depth + 1, False)
                    board[i][j] = ' '
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(5):
            for j in range(5):
                if board[i][j] == ' ':
                    board[i][j] = 'Red'
                    score = minimax(board, depth + 1, True)
                    board[i][j] = ' '
                    best_score = min(score, best_score)
        return best_score

def check_winner(board):
    # Check rows and columns
    for i in range(5):
        if board[i][0] == board[i][1] == board[i][2] == board[i][3] == board[i][4] != ' ':
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] == board[3][i] == board[4][i] != ' ':
            return board[0][i]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] == board[3][3] == board[4][4] != ' ':
        return board[0][0]
    if board[0][4] == board[1][3] == board[2][2] == board[3][1] == board[4][0] != ' ':
        return board[0][4]
    
    return None

def is_board_full(board):
    return all(cell != ' ' for row in board for cell in row)