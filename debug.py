from database import SessionLocal
from models import User, UserRole

session = SessionLocal()

user = session.query(User).filter(User.id == 1).first()  # đổi 1 thành id admin của bạn

print("repr role  :", repr(user.role))
print("type role  :", type(user.role))
print("UserRole.ADMIN:", UserRole.ADMIN)
print("So sánh   :", user.role == UserRole.ADMIN)

session.close()