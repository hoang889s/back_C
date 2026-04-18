import os
class Config:
    # server
    HOST = "127.0.0.1"
    PORT = 8000
    DEBUG = True
    # ai
    AI_DEPTH = 4
    AI_COLOR = "black"
    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key")
    JWT_EXPIRE_MINUTES = 60
    DB_URL = os.getenv("DB_URL", "sqlite:///chess.db")
    ALLOWED_ORIGINS = ["http://localhost:5173"]
    SOCKET_ASYNC_MODE = "threading"