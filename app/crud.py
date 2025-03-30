from sqlalchemy.orm import Session
from .models import Game
from .schemas import GameCreateRequest, MoveRequest, GameState
from .game_logic import initial_board, apply_move, check_winner, board_full, easy_bot_move


def create_game(db: Session, req: GameCreateRequest) -> GameState:
    board = initial_board()
    game = Game(
        player_1=req.player_1,
        player_2=req.player_2,
        board=board,
        current_turn='x',
        status='in_progress'
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return GameState(id=str(game.id), board=board, current_turn='x', status='in_progress')

def make_move(db: Session, game_id: str, move: MoveRequest) -> GameState:
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise Exception("Game not found")

    if game.status != 'in_progress':
        raise Exception("Game already ended")

    board = game.board
    if game.current_turn != move.player:
        raise Exception("Not this player's turn")

    success = apply_move(board, move.row, move.side, move.player)
    if not success:
        raise Exception("Invalid move")

    if check_winner(board, move.player):
        game.status = f"{move.player}_won"
    elif board_full(board):
        game.status = "draw"
    else:
        game.current_turn = 'o' if move.player == 'x' else 'x'

    game.board = board
    db.commit()
    db.refresh(game)

    # Easy bot move if enabled
    if game.player_2 == 'bot' and game.current_turn == 'o':
        bot_move = easy_bot_move(board)
        if bot_move:
            apply_move(board, bot_move[0], bot_move[1], 'o')
            if check_winner(board, 'o'):
                game.status = 'o_won'
            elif board_full(board):
                game.status = 'draw'
            else:
                game.current_turn = 'x'
            game.board = board
            db.commit()
            db.refresh(game)

    return GameState(
        id=str(game.id),
        board=game.board,
        current_turn=game.current_turn,
        status=game.status
    )

def get_game_state(db: Session, game_id: str) -> GameState:
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise Exception("Game not found")
    return GameState(
        id=str(game.id),
        board=game.board,
        current_turn=game.current_turn,
        status=game.status
    )


def delete_game(db: Session, game_id: str) -> bool:
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        return False
    db.delete(game)
    db.commit()
    return True
