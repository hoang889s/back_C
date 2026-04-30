import os
from dotenv import load_dotenv

# load file .env
load_dotenv()

class Config:
    # =============================
    # SERVER
    # =============================
    HOST = "127.0.0.1"
    PORT = 8000
    DEBUG = True

    # =============================
    # AI
    # =============================
    AI_DEPTH = 4
    AI_COLOR = "black"

    # =============================
    # JWT
    # =============================
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRES_MIN", 60))

    # =============================
    # DATABASE (SQL SERVER)
    # =============================
    DB_SERVER = os.getenv("DB_SERVER", "localhost\\SQLEXPRESS")
    DB_NAME = os.getenv("DB_NAME", "chess_online")
    DB_USER = os.getenv("DB_USER", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

    # escape "\" cho Python
    DB_SERVER = DB_SERVER.replace("\\", "\\\\")

    # nếu có user/password → SQL Auth
    if DB_USER and DB_PASSWORD:
        DB_URL = (
            f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
            f"?driver={DB_DRIVER.replace(' ', '+')}"
        )
    else:
        # Windows Authentication
        DB_URL = (
            f"mssql+pyodbc://@{DB_SERVER}/{DB_NAME}"
            f"?driver={DB_DRIVER.replace(' ', '+')}&trusted_connection=yes"
        )

    # =============================
    # CORS
    # =============================
    ALLOWED_ORIGINS = ["http://localhost:5173"]

    # =============================
    # SOCKET
    # =============================
    SOCKET_ASYNC_MODE = "threading"

    # =============================
    # SECRET KEY
    # =============================
    SECRET_KEY = os.getenv("SECRET_KEY", JWT_SECRET)