import random
ROWS = 7
COLS = 7

def initial_board():
    return [["_" for _ in range(COLS)] for _ in range(ROWS)]

def apply_move(board, row, side, symbol):
    if side == 'L':
        for col in range(COLS):
            if board[row][col] == '_':
                board[row][col] = symbol
                return True
    elif side == 'R':
        for col in reversed(range(COLS)):
            if board[row][col] == '_':
                board[row][col] = symbol
                return True
    return False

def check_winner(board, symbol):
    for r in range(ROWS):
        for c in range(COLS):
            if c + 3 < COLS and all(board[r][c+i] == symbol for i in range(4)):
                return True
            if r + 3 < ROWS and all(board[r+i][c] == symbol for i in range(4)):
                return True
            if r + 3 < ROWS and c + 3 < COLS and all(board[r+i][c+i] == symbol for i in range(4)):
                return True
            if r + 3 < ROWS and c - 3 >= 0 and all(board[r+i][c-i] == symbol for i in range(4)):
                return True
    return False

def board_full(board):
    return all(cell != '_' for row in board for cell in row)

def easy_bot_move(board):
    valid_moves = []
    for row in range(ROWS):
        for side in ['L', 'R']:
            temp = [r.copy() for r in board]
            if apply_move(temp, row, side, 'o'):
                valid_moves.append((row, side))
    return random.choice(valid_moves) if valid_moves else None