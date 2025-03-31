import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base
import enum

class PlayerType(str, enum.Enum):
    human = "human"
    easy_bot = "easy_bot"
    medium_bot = "medium_bot"
    hard_bot = "hard_bot"

class Player(Base):
    __tablename__ = "players"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nickname = Column(String, nullable=False)
    type = Column(Enum(PlayerType), nullable=False)

class Game(Base):
    __tablename__ = "games"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_1_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    player_2_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    current_turn = Column(String, default='x')
    board = Column(JSON, nullable=False)
    status = Column(String, default='in_progress')
    created_at = Column(DateTime, default=datetime.utcnow)

    player_1 = relationship("Player", foreign_keys=[player_1_id])
    player_2 = relationship("Player", foreign_keys=[player_2_id])
