import random
import copy
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

def easy_bot_move(board, bot_symbol):
    valid_moves = []
    for row in range(ROWS):
        for side in ['L', 'R']:
            temp = [r.copy() for r in board]
            if apply_move(temp, row, side, bot_symbol):
                valid_moves.append((row, side))
    return random.choice(valid_moves) if valid_moves else None

### MINIMAX ###
def score_window(window, bot_symbol, opponent_symbol):
    counts = {
        bot_symbol: window.count(bot_symbol),
        opponent_symbol: window.count(opponent_symbol),
        '_': window.count('_')
    }

    if counts[bot_symbol] > 0 and counts[opponent_symbol] > 0:
        return 0  # mixed window

    # Scoring table (bot-positive, opponent-negative)
    score_map = {
        (4, 0): 10000,
        (3, 1): 100,
        (2, 2): 10,
        (1, 3): 1,
        (0, 4): -10000,
        (0, 3): -100,
        (0, 2): -10,
        (0, 1): -1,
    }

    key = (counts[bot_symbol], counts['_'])
    return score_map.get(key, 0)

def evaluate_board(board, bot_symbol):
    opponent_symbol = 'o' if bot_symbol == 'x' else 'x'
    score = 0

    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            window = [board[r][c+i] for i in range(4)]
            score += score_window(window, bot_symbol, opponent_symbol)

    # Vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            window = [board[r+i][c] for i in range(4)]
            score += score_window(window, bot_symbol, opponent_symbol)

    # Diagonal ↘
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += score_window(window, bot_symbol, opponent_symbol)

    # Diagonal ↙
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            window = [board[r+i][c-i] for i in range(4)]
            score += score_window(window, bot_symbol, opponent_symbol)

    return score

def minimax_ab(board, depth, alpha, beta, maximizing, bot_symbol):
    opponent_symbol = 'o' if bot_symbol == 'x' else 'x'

    # Terminal conditions
    if check_winner(board, bot_symbol):
        return 10000
    if check_winner(board, opponent_symbol):
        return -10000
    if board_full(board) or depth == 0:
        return evaluate_board(board, bot_symbol)

    if maximizing:
        max_eval = float('-inf')
        for row in range(ROWS):
            for side in ['L', 'R']:
                temp_board = copy.deepcopy(board)
                if apply_move(temp_board, row, side, bot_symbol):
                    eval = minimax_ab(temp_board, depth - 1, alpha, beta, False, bot_symbol)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break  # Beta cut-off
        return max_eval
    else:
        min_eval = float('inf')
        for row in range(ROWS):
            for side in ['L', 'R']:
                temp_board = copy.deepcopy(board)
                if apply_move(temp_board, row, side, opponent_symbol):
                    eval = minimax_ab(temp_board, depth - 1, alpha, beta, True, bot_symbol)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Alpha cut-off
        return min_eval

def medium_bot_move(board, bot_symbol, depth=3):
    best_score = float('-inf')
    best_move = None

    for row in range(ROWS):
        for side in ['L', 'R']:
            temp_board = copy.deepcopy(board)
            if apply_move(temp_board, row, side, bot_symbol):
                score = minimax_ab(temp_board, depth - 1, float('-inf'), float('inf'), False, bot_symbol)
                if score > best_score:
                    best_score = score
                    best_move = (row, side)

    return best_move

### END MINIMAX ###

def hard_bot_move(board, bot_symbol):
    return medium_bot_move(board, bot_symbol)