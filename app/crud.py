import uuid
import random
import time
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from . import models, schemas
from .game_logic import initial_board, apply_move, check_winner, board_full, easy_bot_move, medium_bot_move, hard_bot_move

def create_player(db: Session, player: schemas.PlayerCreate) -> models.Player:
    db_player = models.Player(nickname=player.nickname, type=player.type)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def get_player(db: Session, player_id: uuid.UUID) -> models.Player:
    return db.query(models.Player).filter(models.Player.id == player_id).first()

def delete_player(db: Session, player_id: uuid.UUID):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if player:
        db.delete(player)
        db.commit()
        

def create_game(db: Session, req: schemas.GameCreateRequest) -> models.Game:
    board = initial_board()
    game = models.Game(
        player_1_id=req.player_1_id,
        player_2_id=req.player_2_id,
        board=board,
        current_turn='x',
        status='in_progress'
    )
    db.add(game)
    db.commit()
    db.refresh(game)

    return game

def get_game(db: Session, game_id: uuid.UUID) -> models.Game:
    return db.query(models.Game).filter(models.Game.id == game_id).first()

def get_all_games(db: Session) -> list[models.Game]:
    return db.query(models.Game).all()

def get_all_players(db: Session) -> list[models.Player]:
    return db.query(models.Player).all()

def delete_game(db: Session, game_id: uuid.UUID):
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if game:
        # Delete associated players
        player1 = db.query(models.Player).filter(models.Player.id == game.player_1_id).first()
        player2 = db.query(models.Player).filter(models.Player.id == game.player_2_id).first()
        if player1:
            db.delete(player1)
        if player2:
            db.delete(player2)

        db.delete(game)
        db.commit()


def make_move(db: Session, game_id: uuid.UUID, move: schemas.Move) -> models.Game:
    game = get_game(db, game_id)
    if game.status != 'in_progress':
        return game
    
    if move.player != game.current_turn:
        return game

    board = game.board
    symbol = move.player
    success = apply_move(board, move.row, move.side, symbol)
    if not success:
        return game

    if check_winner(board, symbol):
        game.status = f"{symbol}_won"
    elif board_full(board):
        game.status = "draw"
    else:
        game.current_turn = 'o' if symbol == 'x' else 'x'

    game.board = board
    flag_modified(game, "board")
    db.commit()
    db.refresh(game)
    return game

def get_bot_move(db: Session, game_id: uuid.UUID, difficulty: str):
    game = get_game(db, game_id)
    board = game.board
    bot_symbol = game.current_turn  # bot's symbol based on turn

    if difficulty == 'easy_bot':
        return easy_bot_move(board, bot_symbol)
    elif difficulty == 'medium_bot':
        return medium_bot_move(board, bot_symbol)
    elif difficulty == 'hard_bot':
        return hard_bot_move(board, bot_symbol)
    else:
        return None