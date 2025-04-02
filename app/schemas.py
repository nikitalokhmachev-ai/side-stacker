from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from enum import Enum

class PlayerType(str, Enum):
    human = "human"
    easy_bot = "easy_bot"
    medium_bot = "medium_bot"
    hard_bot = "hard_bot"

class PlayerCreate(BaseModel):
    nickname: str
    type: PlayerType

class PlayerInfo(BaseModel):
    id: UUID
    nickname: str
    type: PlayerType

class Move(BaseModel):
    player: str
    row: int
    side: str  # 'L' or 'R'

class GameCreateRequest(BaseModel):
    player_1_id: UUID
    player_2_id: UUID

class GameState(BaseModel):
    id: str
    board: List[List[str]]
    current_turn: str
    status: str
    player_1: PlayerInfo
    player_2: PlayerInfo