import random

def get_best_move(board):
    # Check for winning move
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'Green'
                if check_winner(board) == 'Green':
                    board[i][j] = ' '
                    return (i, j)
                board[i][j] = ' '

    # Check for blocking move
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'Red'
                if check_winner(board) == 'Red':
                    board[i][j] = ' '
                    return (i, j)
                board[i][j] = ' '

    # Try to take center
    if board[1][1] == ' ':
        return (1, 1)

    # Try to take corners
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    random.shuffle(corners)
    for corner in corners:
        if board[corner[0]][corner[1]] == ' ':
            return corner

    # Take any available edge
    edges = [(0, 1), (1, 0), (1, 2), (2, 1)]
    random.shuffle(edges)
    for edge in edges:
        if board[edge[0]][edge[1]] == ' ':
            return edge

    return None

def check_winner(board):
    # Check rows and columns
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != ' ':
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != ' ':
            return board[0][i]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]
    
    return None
