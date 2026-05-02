from sqlalchemy import (
    Column, Integer, String, Text,
    ForeignKey, Enum as SAEnum, Boolean
)
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from persistence.database import Base

# ================= ENUM =================

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class GameMode(str, enum.Enum):
    AI = "ai"
    HUMAN = "human"

class GameResult(str, enum.Enum):
    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"
    ONGOING = "ongoing"

class RoomStatus(str, enum.Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"

class Turn(str, enum.Enum):
    WHITE = "white"
    BLACK = "black"

_by_value = lambda x: [e.value for e in x]

# ================= USER =================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    role = Column(
        SAEnum(UserRole, values_callable=_by_value),
        default=UserRole.USER,
        nullable=False
    )

    created_at = Column(DATETIME2, server_default=func.now())

    games_as_white = relationship(
        "Game",
        foreign_keys="Game.white_player_id",
        back_populates="white_player"
    )

    games_as_black = relationship(
        "Game",
        foreign_keys="Game.black_player_id",
        back_populates="black_player"
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"

# ================= ROOM =================

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    is_private = Column(Boolean, default=False)
    password_hash = Column(String(255), nullable=True)

    status = Column(
        SAEnum(RoomStatus, values_callable=_by_value),
        default=RoomStatus.WAITING,
        nullable=False,
    )

    mode = Column(
        SAEnum(GameMode, values_callable=_by_value),
        nullable=False
    )

    time_limit = Column(Integer, default=600)
    player_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DATETIME2, server_default=func.now())

    # relationships
    owner = relationship("User")

    players = relationship(
        "RoomPlayer",
        back_populates="room",
        cascade="all, delete-orphan"
    )

    # ❗ chỉ reference từ Game (KHÔNG có FK ở đây)
    game = relationship(
        "Game",
        back_populates="room",
        uselist=False
    )

# ================= ROOM PLAYER =================

class RoomPlayer(Base):
    __tablename__ = "room_players"

    id = Column(Integer, primary_key=True)

    room_id = Column(
        Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    role = Column(String(20), default="player")
    joined_at = Column(DATETIME2, server_default=func.now())

    # relationships
    room = relationship("Room", back_populates="players")
    user = relationship("User")

# ================= GAME =================

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)

    # ✅ CHỈ 1 FK duy nhất tới Room
    room_id = Column(
        Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        unique=True   # đảm bảo 1 room chỉ có 1 game
    )

    white_player_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    black_player_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    fen = Column(Text, default="startpos")

    turn = Column(
        SAEnum(Turn, values_callable=_by_value),
        default=Turn.WHITE,
        nullable=False
    )

    status = Column(
        SAEnum(GameResult, values_callable=_by_value),
        default=GameResult.ONGOING,
        nullable=False
    )

    created_at = Column(DATETIME2, server_default=func.now())

    # relationships
    room = relationship("Room", back_populates="game")

    white_player = relationship(
        "User",
        foreign_keys=[white_player_id],
        back_populates="games_as_white"
    )

    black_player = relationship(
        "User",
        foreign_keys=[black_player_id],
        back_populates="games_as_black"
    )

    moves = relationship(
        "Move",
        back_populates="game",
        cascade="all, delete-orphan",
        order_by="Move.move_number"
    )

# ================= MOVE =================

class Move(Base):
    __tablename__ = "moves"

    id = Column(Integer, primary_key=True)

    game_id = Column(
        Integer,
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False
    )

    move = Column(String(20), nullable=False)
    move_number = Column(Integer)

    player_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(DATETIME2, server_default=func.now())

    # relationships
    game = relationship("Game", back_populates="moves")
    player = relationship("User")