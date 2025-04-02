from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from uuid import UUID
from .. import crud, schemas, models
from ..database import SessionLocal

router = APIRouter()

sessions = {}  # game_id -> {"players": set(websockets), "spectators": set(websockets)}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/players", response_model=schemas.PlayerInfo)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = crud.create_player(db, player)
    return schemas.PlayerInfo(id=db_player.id, nickname=db_player.nickname, type=db_player.type)

@router.post("/create", response_model=schemas.GameState)
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

@router.get("/{game_id}", response_model=schemas.GameState)
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

@router.get("/games", response_model=list[schemas.GameState])
def get_all_games(db: Session = Depends(get_db)):
    games = crud.get_games(db)
    return [schemas.GameState(
                id=str(game.id),
                board=game.board,
                current_turn=game.current_turn,
                status=game.status,
                player_1=schemas.PlayerInfo(
                    id=game.player_1.id, nickname=game.player_1.nickname, type=game.player_1.type),
                player_2=schemas.PlayerInfo(
                    id=game.player_2.id, nickname=game.player_2.nickname, type=game.player_2.type)
                ) for game in games]

@router.post("/{game_id}/move", response_model=schemas.GameState)
def make_move(game_id: UUID, move: schemas.Move, db: Session = Depends(get_db)):
    game = crud.make_move(db, game_id, move)
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

@router.post("/{game_id}/bot/{difficulty}", response_model=schemas.GameState)
def make_bot_move(game_id: UUID, difficulty: str, db: Session = Depends(get_db)):
    bot_move = crud.get_bot_move(db, game_id, difficulty)
    if not bot_move:
        raise HTTPException(status_code=404, detail="Difficulty not found.")

    move = schemas.Move(player=game.current_turn, row=bot_move[0], side=bot_move[1])
    game = crud.make_move(db, game_id, move)
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

@router.delete("/{game_id}")
def delete_game(game_id: UUID, db: Session = Depends(get_db)):
    crud.delete_game(db, game_id)
    return {"detail": f"Game {game_id} deleted"}

@router.websocket("/ws/{game_id}/{client_type}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, client_type: str):
    await websocket.accept()
    if game_id not in sessions:
        sessions[game_id] = {"players": set(), "spectators": set()}

    if client_type in ["player1", "player2"]:
        sessions[game_id]["players"].add(websocket)
    else:
        sessions[game_id]["spectators"].add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            for ws in sessions[game_id]["players"].union(sessions[game_id]["spectators"]):
                if ws is not websocket:
                    await ws.send_text(data)
    except WebSocketDisconnect:
        sessions[game_id]["players"].discard(websocket)
        sessions[game_id]["spectators"].discard(websocket)
        if not sessions[game_id]["players"] and not sessions[game_id]["spectators"]:
            del sessions[game_id]
