from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request
from sqlalchemy.orm import Session
from uuid import UUID
from .. import crud, schemas, models
from ..database import SessionLocal
from typing import List, Dict, Set, Optional
import json
from fastapi.encoders import jsonable_encoder
from collections import deque
from threading import Lock
from dataclasses import dataclass
from typing import Optional

router = APIRouter()

# In-memory connection store per game
game_connections: Dict[UUID, Set[WebSocket]] = {}

@dataclass
class WaitingPlayer:
    id: UUID
    websocket: WebSocket

waiting_player: Optional[WaitingPlayer] = None
waiting_lock = Lock()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/games", response_model=List[schemas.GameState])
def get_all_games(db: Session = Depends(get_db)):
    games = crud.get_all_games(db)
    return [schemas.GameState(
        id=str(game.id), 
        player_1=schemas.PlayerInfo(id=game.player_1.id, nickname=game.player_1.nickname, type=game.player_1.type),
        player_2=schemas.PlayerInfo(id=game.player_2.id, nickname=game.player_2.nickname, type=game.player_2.type),
        current_turn=game.current_turn,
        board=game.board,
        status=game.status) 
        for game in games]

@router.get("/api/games/{game_id}", response_model=schemas.GameState)
def get_game_state(game_id: UUID, db: Session = Depends(get_db)):
    game = crud.get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
    return schemas.GameState(
        id=str(game.id),
        board=game.board,
        current_turn=game.current_turn,
        status=game.status,
        player_1=schemas.PlayerInfo(
            id=game.player_1.id, nickname=game.player_1.nickname, type=game.player_1.type),
        player_2=schemas.PlayerInfo(
            id=game.player_2.id, nickname=game.player_2.nickname, type=game.player_2.type)
    )

@router.post("/api/game", response_model=schemas.GameState)
def create_game(req: schemas.GameCreateRequest, db: Session = Depends(get_db)):
    game = crud.create_game(db, req)
    return schemas.GameState(
        id=str(game.id),
        board=game.board,
        current_turn=game.current_turn,
        status=game.status,
        player_1=schemas.PlayerInfo(
            id=game.player_1.id, nickname=game.player_1.nickname, type=game.player_1.type),
        player_2=schemas.PlayerInfo(
            id=game.player_2.id, nickname=game.player_2.nickname, type=game.player_2.type)
    )

@router.post("/api/games/{game_id}/move", response_model=schemas.GameState)
async def make_move(game_id: UUID, move: schemas.Move, db: Session = Depends(get_db)):
    game = crud.make_move(db, game_id, move)
    game_state = schemas.GameState(
        id=str(game.id),
        board=game.board,
        current_turn=game.current_turn,
        status=game.status,
        player_1=schemas.PlayerInfo(
            id=game.player_1.id, nickname=game.player_1.nickname, type=game.player_1.type),
        player_2=schemas.PlayerInfo(
            id=game.player_2.id, nickname=game.player_2.nickname, type=game.player_2.type)
    )

    # Broadcast to WebSocket clients
    if game_id in game_connections:
        message = json.dumps(jsonable_encoder(game_state))
        to_remove = set()
        for connection in game_connections[game_id]:
            try:
                await connection.send_text(message)
            except Exception:
                to_remove.add(connection)
        game_connections[game_id] -= to_remove

    return game_state

@router.post("/api/games/{game_id}/bot_move/{difficulty}", response_model=schemas.GameState)
async def make_bot_move(game_id: UUID, difficulty: str, db: Session = Depends(get_db)):
    bot_move = crud.get_bot_move(db, game_id, difficulty)
    game = crud.get_game(db, game_id)
    if not bot_move:
        raise HTTPException(status_code=404, detail="Difficulty not found.")

    move = schemas.Move(player=game.current_turn, row=bot_move[0], side=bot_move[1])
    game = crud.make_move(db, game_id, move)
    game_state = schemas.GameState(
        id=str(game.id),
        board=game.board,
        current_turn=game.current_turn,
        status=game.status,
        player_1=schemas.PlayerInfo(
            id=game.player_1.id, nickname=game.player_1.nickname, type=game.player_1.type),
        player_2=schemas.PlayerInfo(
            id=game.player_2.id, nickname=game.player_2.nickname, type=game.player_2.type)
    )

    # Broadcast to WebSocket clients
    if game_id in game_connections:
        message = json.dumps(jsonable_encoder(game_state))
        to_remove = set()
        for connection in game_connections[game_id]:
            try:
                await connection.send_text(message)
            except Exception:
                to_remove.add(connection)
        game_connections[game_id] -= to_remove

    return game_state

@router.delete("/api/games/{game_id}")
async def delete_game(game_id: UUID, db: Session = Depends(get_db)):
    crud.delete_game(db, game_id)
    # Notify connected clients that the game was deleted
    if game_id in game_connections:
        message = json.dumps({
            "id": str(game_id),
            "status": "deleted"
        })

        to_remove = set()
        for connection in game_connections[game_id]:
            try:
                await connection.send_text(message)
            except:
                to_remove.add(connection)

        game_connections[game_id] -= to_remove
        if not game_connections[game_id]:
            del game_connections[game_id]
    return {"detail": f"Game {game_id} deleted"}

@router.get("/api/players", response_model=List[schemas.PlayerInfo])
def get_all_players(db: Session = Depends(get_db)):
    players = crud.get_all_players(db)
    return [schemas.PlayerInfo(id=player.id, nickname=player.nickname, type=player.type) for player in players]

@router.get("/api/players/{player_id}", response_model=schemas.PlayerInfo)
def get_player(player_id: UUID, db: Session = Depends(get_db)):
    player = crud.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
    return schemas.PlayerInfo(id=player.id, nickname=player.nickname, type=player.type)

@router.post("/api/player", response_model=schemas.PlayerInfo)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = crud.create_player(db, player)
    return schemas.PlayerInfo(id=db_player.id, nickname=db_player.nickname, type=db_player.type)

@router.delete("/api/players/{player_id}")
def delete_player(player_id: UUID, db: Session = Depends(get_db)):
    crud.delete_player(db, player_id)
    return {"detail": f"Player {player_id} deleted"}

async def websocket_endpoint(websocket: WebSocket, game_id: UUID):
    await websocket.accept()
    if game_id not in game_connections:
        game_connections[game_id] = set()
    game_connections[game_id].add(websocket)

    try:
        while True:
            await websocket.receive_text()  # no-op for now
    except WebSocketDisconnect:
        game_connections[game_id].remove(websocket)
        if not game_connections[game_id]:
            del game_connections[game_id]


@router.websocket("/ws/waiting/{player_id}")
async def waiting_room_ws(websocket: WebSocket, player_id: UUID):
    global waiting_player
    await websocket.accept()

    with waiting_lock:
        waiting_player = WaitingPlayer(id=player_id, websocket=websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        with waiting_lock:
            if waiting_player and waiting_player.id == player_id:
                waiting_player = None


@router.post("/api/online-game")
async def find_online_game(request: Request, db: Session = Depends(get_db)):
    global waiting_player
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    player_id = UUID(data["player_id"])

    with waiting_lock:
        if waiting_player and waiting_player.id != player_id:
            opponent = waiting_player
            waiting_player = None

            req = schemas.GameCreateRequest(player_1_id=opponent.id, player_2_id=player_id)
            game = crud.create_game(db, req)

            game_state = schemas.GameState(
                id=str(game.id),
                board=game.board,
                current_turn=game.current_turn,
                status=game.status,
                player_1=schemas.PlayerInfo(
                    id=game.player_1.id, nickname=game.player_1.nickname, type=game.player_1.type),
                player_2=schemas.PlayerInfo(
                    id=game.player_2.id, nickname=game.player_2.nickname, type=game.player_2.type)
            )

            try:
                await opponent.websocket.send_text(json.dumps(jsonable_encoder(game_state)))
            except:
                pass  # If they're disconnected, we just fail silently

            return {
                "waiting": False,
                "game": jsonable_encoder(game_state)
            }

        return { "waiting": True }
