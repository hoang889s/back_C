#from sqlalchemy import Nullable
from sqlalchemy import (
    Column, Integer, String, DateTime, Text,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base
# trạng thái ván đầu
class GameResult(str,enum.Enum):
    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"
    ONGOING = "ongoing"
# bảng user
class User(Base):
    __tablename__ ="users"
    id = Column(Integer,primary_key=True,index= True)
    username = Column(String(50),unique=True,nullable=False,index=True)
    email = Column(String(120),unique=True,nullable=False,index=True)
    password_hash = Column(String(255),nullable=False)
    created_at = Column(DATETIME2, server_default=func.now())
    games_as_white = relationship(
        "GameHistory",foreign_keys = "GameHistory.white_player_id",back_populates = "white_player"
    )
    games_as_black = relationship(
        "GameHistory",foreign_keys = "GameHistory.black_player_id",back_populates = "black_player" 
    )
    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"
# bảng GameHistory lưu kết quả mỗi ván đấu
class GameHistory(Base):
    __tablename__ = "game_history"
    id = Column(Integer,primary_key = True,index = True)
    # null = AI
    white_player_id = Column(Integer,ForeignKey("users.id"),nullable=True)
    black_player_id = Column(Integer,ForeignKey("users.id"),nullable=True)
    result = Column(SAEnum(GameResult),default = GameResult.ONGOING,nullable=False)
    pgn_moves = Column(Text,nullable=True)
    total_moves = Column(Integer,default=0)
    started_at = Column(DateTime(timezone=True),server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    white_player = relationship("User",foreign_keys = [white_player_id],back_populates = "games_as_white")
    black_player = relationship("User",foreign_keys = [black_player_id],back_populates = "games_as_black")
    def __repr__(self):
        return f"<GameHistory id ={self.id} result ={self.result}>"