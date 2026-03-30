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
# phân quyền
class UserRole(str,enum.Enum):
    ADMIN = "admin"
    USER = "user"
# trạng thái ván đầu
class GameResult(str,enum.Enum):
    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"
    ONGOING = "ongoing"
_by_value = lambda x: [e.value for e in x]
# bảng user
class User(Base):
    __tablename__ ="users"
    id = Column(Integer,primary_key=True,index= True)
    username = Column(String(50),unique=True,nullable=False,index=True)
    email = Column(String(120),unique=True,nullable=False,index=True)
    password_hash = Column(String(255),nullable=False)
    role = Column(SAEnum(UserRole,values_callable=_by_value), default=UserRole.USER, nullable=False)
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
    result = Column(SAEnum(GameResult, values_callable=_by_value), default=GameResult.ONGOING, nullable=False)
    pgn_moves = Column(Text,nullable=True)
    total_moves = Column(Integer,default=0)
    started_at = Column(DateTime(timezone=True),server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    white_player = relationship("User",foreign_keys = [white_player_id],back_populates = "games_as_white")
    black_player = relationship("User",foreign_keys = [black_player_id],back_populates = "games_as_black")
    def __repr__(self):
        return f"<GameHistory id ={self.id} result ={self.result}>"
# phần room
# trạng thái phòng
class RoomStatus(str, enum.Enum):
    # chờ
    WAITING = "waiting"
    # đang đấu
    PLAYING = "playing"
    # kết thúc
    FINISHED = "finished"
    # bị bỏ
    ABANDONED = "abandoned"
# chế độ phòng
class RoomMode(str, enum.Enum):
    # người với người
    PVP = "pvp"
    # người với máy
    PVA = "pva"
# bảng dữ liệu room

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer,primary_key=True,index = True)
    # được trùng nhau về mã phòng
    code = Column(String(8),unique=True,nullable=False,index=True)
    host_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    guest_id = Column(Integer,ForeignKey("users.id"),nullable=True)
    # nó sẽ lưu pvp thay PVP
    mode = Column(SAEnum(RoomMode,values_callable=_by_value),default=RoomMode.PVP,nullable=False)
    status = Column(SAEnum(RoomStatus,values_callable=_by_value),default=RoomStatus.WAITING,nullable=False)
    # white|black
    host_color = Column(String(5),default="white",nullable=False)
    password_hash = Column(String(255),nullable=True)
    # giới hình thời gian
    time_limit = Column(Integer,nullable=True)
    game_id = Column(Integer,ForeignKey("game_history.id"),nullable=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    started_at = Column(DateTime(timezone=True),nullable=True)
    ended_at = Column(DateTime(timezone=True),nullable=True)
    # quan hệ
    host = relationship("User",foreign_keys = [host_id])
    guest = relationship("User",foreign_keys=[guest_id])
    game = relationship("GameHistory", foreign_keys=[game_id])

    def __repr__(self):
        return f"<Room code={self.code} status={self.status}>"
