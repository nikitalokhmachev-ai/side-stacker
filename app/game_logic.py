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
            temp = copy.deepcopy(board)
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

    score_map = {
        (4, 0): 10000,
        (3, 1): 1000,    # increased for stronger threat recognition
        (2, 2): 100,
        (1, 3): 10,
        (0, 4): -100000,  # huge penalty for allowing a win
        (0, 3): -10000,
        (0, 2): -500,
        (0, 1): -50
    }

    key = (counts[bot_symbol], counts['_'])
    return score_map.get(key, 0)

def check_blocking_move(board, bot_symbol):
    opponent_symbol = 'o' if bot_symbol == 'x' else 'x'
    for row in range(ROWS):
        for side in ['L', 'R']:
            temp_board = copy.deepcopy(board)
            if apply_move(temp_board, row, side, opponent_symbol):
                if check_winner(temp_board, opponent_symbol):
                    return (row, side)
    return None

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

def minimax_smart(board, depth, maximizing, bot_symbol):
    opponent_symbol = 'o' if bot_symbol == 'x' else 'x'

    if check_winner(board, bot_symbol):
        return 10000 + depth
    if check_winner(board, opponent_symbol):
        return -100000 - (10 * depth)  # make losses harsher the sooner they happen
    if board_full(board) or depth == 0:
        return evaluate_board(board, bot_symbol)

    if maximizing:
        max_eval = float('-inf')
        for row in range(ROWS):
            for side in ['L', 'R']:
                temp_board = copy.deepcopy(board)
                if apply_move(temp_board, row, side, bot_symbol):
                    eval = minimax_smart(temp_board, depth - 1, False, bot_symbol)
                    max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for row in range(ROWS):
            for side in ['L', 'R']:
                temp_board = copy.deepcopy(board)
                if apply_move(temp_board, row, side, opponent_symbol):
                    eval = minimax_smart(temp_board, depth - 1, True, bot_symbol)
                    min_eval = min(min_eval, eval)
        return min_eval

def medium_bot_move(board, bot_symbol, depth=3):
    best_score = float('-inf')
    best_move = None

    # First, check if we must block a win
    blocking_move = check_blocking_move(board, bot_symbol)
    if blocking_move:
        print("🚨 Blocking move detected:", blocking_move)
        return blocking_move

    for row in range(ROWS):
        for side in ['L', 'R']:
            temp_board = copy.deepcopy(board)
            if apply_move(temp_board, row, side, bot_symbol):
                score = minimax_smart(temp_board, depth - 1, False, bot_symbol)
                if score > best_score:
                    best_score = score
                    best_move = (row, side)

    return best_move

### END MINIMAX ###

def hard_bot_move(board, bot_symbol):
    return medium_bot_move(board, bot_symbol)