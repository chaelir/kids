import math
import random

def minimax(board, depth, alpha, beta, is_maximizing):
    scores = {'Red': -1, 'Green': 1, 'Tie': 0}
    
    winner = check_winner(board)
    if winner:
        return scores[winner]
    
    if depth == 0:
        return evaluate_board(board)
    
    if is_maximizing:
        best_score = -math.inf
        for move in get_available_moves(board):
            board[move[0]][move[1]] = 'Green'
            score = minimax(board, depth - 1, alpha, beta, False)
            board[move[0]][move[1]] = ' '
            best_score = max(score, best_score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = math.inf
        for move in get_available_moves(board):
            board[move[0]][move[1]] = 'Red'
            score = minimax(board, depth - 1, alpha, beta, True)
            board[move[0]][move[1]] = ' '
            best_score = min(score, best_score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score

def get_best_move(board):
    best_score = -math.inf
    best_moves = []
    available_moves = get_available_moves(board)
    
    if len(available_moves) > 12:  # If more than 12 moves are available, choose randomly
        return random.choice(available_moves)
    
    for move in available_moves:
        board[move[0]][move[1]] = 'Green'
        score = minimax(board, 3, -math.inf, math.inf, False)  # Depth limited to 3
        board[move[0]][move[1]] = ' '
        if score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)
    
    return random.choice(best_moves)  # Randomly choose from equally good moves

def get_available_moves(board):
    return [(i, j) for i in range(4) for j in range(4) if board[i][j] == ' ']

def evaluate_board(board):
    score = 0
    lines = (
        # Rows
        [board[i][j] for j in range(4)] for i in range(4)
    ) + (
        # Columns
        [board[i][j] for i in range(4)] for j in range(4)
    ) + (
        # Diagonals
        [board[i][i] for i in range(4)],
        [board[i][3-i] for i in range(4)]
    )
    
    for line in lines:
        score += evaluate_line(line)
    
    return score

def evaluate_line(line):
    if line.count('Green') == 3 and line.count(' ') == 1:
        return 10
    elif line.count('Red') == 3 and line.count(' ') == 1:
        return -10
    elif line.count('Green') == 2 and line.count(' ') == 2:
        return 5
    elif line.count('Red') == 2 and line.count(' ') == 2:
        return -5
    return 0

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
    
    if all(cell != ' ' for row in board for cell in row):
        return 'Tie'
    return None
