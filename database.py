import abc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool
import os
# Cấu hình sqlserver 
# tên server hoặc ip
DB_SERVER = os.getenv("DB_SERVER","localhost\\SQLEXPRESS")
# tên database
DB_NAME = os.getenv("DB_NAME","chess_online")
# sa
DB_USER = os.getenv("DB_USER","sa")
# mật khẩu
DB_PASSWORD = os.getenv("DB_PASSWORD","hoang123")
DB_DRIVER = os.getenv("DB_DRIVER","ODBC Driver 17 for SQL Server")
# kết nối với server
# c1
DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
    f"?driver={DB_DRIVER.replace(' ', '+')}&TrustServerCertificate=yes"
)
# -- Cách 2: Windows Authentication (uncomment nếu dùng SSMS với Windows Auth)
# DATABASE_URL = (
#     f"mssql+pyodbc://@{DB_SERVER}/{DB_NAME}"
#     f"?driver={DB_DRIVER.replace(' ', '+')}&trusted_connection=yes"
# )
engine = create_engine(
    DATABASE_URL,
    # tránh lỗi timeout trên SQL server
    poolclass = NullPool,
    # đặt true để xem sql query trong console
    echo = False,
    fast_executemany=True
)
SessionLocal=  sessionmaker(engine,autocommit=False,autoflush=False )
class Base(DeclarativeBase):
    pass
# Helper: lấy session (dùng trong route)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def init_db():
    # import để Base biết về các model
    from models import User, RoomPlayer,Room,Game,Move
    Base.metadata.create_all(bind=engine)
    print("[DB] Đã khởi tạo schema thành công.")
