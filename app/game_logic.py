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

# def apply_move(board, row, side, symbol):
#     if side == 'L':
#         # Insert symbol at the leftmost position and shift right
#         for col in range(COLS):
#             if board[row][col] == '_':
#                 board[row][col] = symbol
#                 break
#             elif col == COLS - 1:
#                 return False  # No space to insert
#         for shift_col in range(col, 0, -1):
#             board[row][shift_col] = board[row][shift_col - 1]
#         board[row][0] = symbol
#         return True

#     elif side == 'R':
#         # Insert symbol at the rightmost position and shift left
#         for col in range(COLS - 1, -1, -1):
#             if board[row][col] == '_':
#                 board[row][col] = symbol
#                 break
#             elif col == 0:
#                 return False  # No space to insert
#         for shift_col in range(col, COLS - 1):
#             board[row][shift_col] = board[row][shift_col + 1]
#         board[row][COLS - 1] = symbol
#         return True

#     return False


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


# def find_winning_move(board, bot_symbol):
#     opponent_symbol = 'o' if bot_symbol == 'x' else 'x'
#     for row in range(ROWS):
#         for side in ['L', 'R']:
#             temp_board = copy.deepcopy(board)
#             if apply_move(temp_board, row, side, opponent_symbol):
#                 if check_winner(temp_board, opponent_symbol):
#                     return (row, side)
#     return None

def find_winning_move(board, symbol):
    for row in range(ROWS):
        for side in ['L', 'R']:
            temp_board = copy.deepcopy(board)
            if apply_move(temp_board, row, side, symbol):
                if check_winner(temp_board, symbol):
                    return (row, side)
    return None


def easy_bot_move(board, bot_symbol):
    # Check for immediate threat to block
    opponent_symbol = 'o' if bot_symbol == 'x' else 'x'

    # 1. Try to win
    winning_move = find_winning_move(board, bot_symbol)
    if winning_move:
        return winning_move

    # 2. Block opponent's win
    block_move = find_winning_move(board, opponent_symbol)
    if block_move:
        return block_move

    # 3. Else, make random move
    valid_moves = []
    for row in range(ROWS):
        for side in ['L', 'R']:
            temp = copy.deepcopy(board)
            if apply_move(temp, row, side, bot_symbol):
                valid_moves.append((row, side))
    return random.choice(valid_moves) if valid_moves else None

### MINIMAX ###
def score_window(window, bot_symbol, opponent_symbol):
    bot_count = window.count(bot_symbol)
    opp_count = window.count(opponent_symbol)

    if bot_count > 0 and opp_count > 0:
        return 0  # mixed window, no threat

    if bot_count > 0:
        return bot_count  # 1 to 4
    elif opp_count > 0:
        return -opp_count  # -1 to -4
    return 0


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

def minimax_smart(board, depth, maximizing, bot_symbol, alpha=float('-inf'), beta=float('inf')):
    opponent_symbol = 'o' if bot_symbol == 'x' else 'x'

    # if check_winner(board, bot_symbol):
    #     return 10000
    # if check_winner(board, opponent_symbol):
    #     return -100000
    if board_full(board) or depth == 0:
        return evaluate_board(board, bot_symbol)

    if maximizing:
        max_eval = float('-inf')
        for row in range(ROWS):
            for side in ['L', 'R']:
                temp_board = copy.deepcopy(board)
                if apply_move(temp_board, row, side, bot_symbol):
                    eval = minimax_smart(temp_board, depth - 1, False, bot_symbol, alpha, beta)
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
                    eval = minimax_smart(temp_board, depth - 1, True, bot_symbol, alpha, beta)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Alpha cut-off
        return min_eval


def medium_bot_move(board, bot_symbol, depth=3):
    opponent_symbol = 'o' if bot_symbol == 'x' else 'x'

    # 1. Try to win
    winning_move = find_winning_move(board, bot_symbol)
    if winning_move:
        return winning_move

    # 2. Block opponent's win
    block_move = find_winning_move(board, opponent_symbol)
    if block_move:
        return block_move

    # 3. Else, use minimax
    best_score = float('-inf')
    best_move = None
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