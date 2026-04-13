import secrets
from models import Room,RoomPlayer
from sqlalchemy.orm import Session
class RoomService:
    def __init__(self,db:Session):
        self.db = db
    # Tạo phòng
    def create_room(self, user, data):
        room = Room(
            name = data["name"],
            code = secrets.token_hex(4),
            owner_id = user.id,
            is_private = data.get("is_private",False),
            password_hash=self._hash_pw(data.get("password"))
        )
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)

        self.db.add(RoomPlayer(room_id=room.id, user_id=user.id))
        self.db.commit()
        return room
    # Vào phòng
    def join_room(self,user,code,password=None):
        room = self.db.query(Room).filter_by(code=code).first()
        if not room:
            raise Exception("Không tồn tại phòng")
        # kiểm tra có bị mật không
        if room.is_private:
            if not self._verify_pw(password, room.password_hash):
                raise Exception("Sai mật khẩu")
        exist = self.db.query(RoomPlayer).filter_by(room_id=room.id,user_id=user.id).first()
        if exist:
            return room
        rp = RoomPlayer(room_id=room.id, user_id=user.id)
        self.db.add(rp)
        self.db.commit()
        return room
    # rời phòng
    def leave_room(self,user,room_id):
        rp = self.db.query(RoomPlayer).filter_by(room_id=room_id,user_id=user.id).first()
        if not rp:
            raise Exception("Không ở trong phòng")
        self.db.delete(rp)
        self.db.commit()
    # công cụ hỗ trợ
    def _hash_pw(self,pw):
        if not pw:
            return None
        import bcrypt
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    def _verify_pw(self, pw, hash_pw):
        if not hash_pw:
            return True
        import bcrypt
        return bcrypt.checkpw(pw.encode(), hash_pw.encode())
