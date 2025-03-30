from pydantic import BaseModel
from typing import List

class MoveRequest(BaseModel):
    player: str
    row: int
    side: str  # 'L' or 'R'

class GameCreateRequest(BaseModel):
    player_1: str
    player_2: str

class GameState(BaseModel):
    id: str
    board: List[List[str]]
    current_turn: str
    status: str