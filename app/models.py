import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class Game(Base):
    __tablename__ = "games"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_1 = Column(String, nullable=False)
    player_2 = Column(String, nullable=False)
    current_turn = Column(String, default='x')
    board = Column(JSON, nullable=False)
    status = Column(String, default='in_progress')
    created_at = Column(DateTime, default=datetime.utcnow)