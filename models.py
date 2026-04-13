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
    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"
class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_private = Column(Integer, default=0)
    password_hash = Column(String(255), nullable=True)
    status = Column(String(20), default="waiting")
    created_at = Column(DATETIME2, server_default=func.now())
    # relationship
    owner = relationship("User")
    players = relationship("RoomPlayer", back_populates="room", cascade="all, delete")
class RoomPlayer(Base):
    __tablename__ = "room_players"
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(String(20), default="player")
    joined_at = Column(DATETIME2, server_default=func.now())
    # relationship
    room = relationship("Room", back_populates="players")
    user = relationship("User")
    
