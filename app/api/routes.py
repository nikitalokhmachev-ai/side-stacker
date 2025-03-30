from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/game", response_model=schemas.GameState)
def create_game(req: schemas.GameCreateRequest, db: Session = Depends(get_db)):
    try:
        return crud.create_game(db, req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/game/{game_id}/move", response_model=schemas.GameState)
def make_move(game_id: str, move: schemas.MoveRequest, db: Session = Depends(get_db)):
    try:
        return crud.make_move(db, game_id, move)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/game/{game_id}", response_model=schemas.GameState)
def get_game_state(game_id: str, db: Session = Depends(get_db)):
    try:
        return crud.get_game_state(db, game_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 
    
@router.delete("/game/{game_id}")
def delete_game(game_id: str, db: Session = Depends(get_db)):
    success = crud.delete_game(db, game_id)
    if not success:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"detail": "Game deleted successfully"}
