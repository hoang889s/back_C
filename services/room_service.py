import secrets
from models import Room, RoomPlayer
from sqlalchemy.orm import Session
class RoomService:
    def __init__(self, db: Session):
        self.db = db
    # tạo phòng
    def create_room(self, user, data):
        if not data or "name" not in data:
            raise Exception("Thiếu tên phòng")
        room = Room(
            name=data["name"],
            code=secrets.token_hex(4),
            owner_id=user.id,
            is_private=1 if data.get("is_private", False) else 0,
            mode=data.get("mode", "human"),
            time_limit=int(data.get("time_limit", 600)),
            password_hash=self._hash_pw(data.get("password")),
            status="waiting"
        )
        self.db.add(room)
        self.db.flush()
        self.db.add(RoomPlayer(
            room_id=room.id,
            user_id=user.id
        ))
        self.db.commit()
        self.db.refresh(room)
        return room
    def join_room(self, user, code, password=None):
        room = self.db.query(Room).filter_by(code=code).first()
        if not room:
            raise Exception("Không tồn tại phòng")
        if room.status != "waiting":
            raise Exception("Phòng đã bắt đầu")
        player_count = self.db.query(RoomPlayer).filter_by(room_id=room.id).count()
        if player_count >= 2:
            raise Exception("Phòng đã đầy")
        if room.is_private:
            if not password or not self._verify_pw(password, room.password_hash):
                raise Exception("Sai mật khẩu")
        exist = self.db.query(RoomPlayer).filter_by(
            room_id = room.id,
            user_id = user.id
        ).first()
        if exist:
            return room
        self.db.add(RoomPlayer(
            room_id=room.id,
            user_id=user.id
        ))
        if player_count + 1 == 2:
            room.status = "playing"
        self.db.commit()
        return room
    def leave_room(self,user,room_id):
        room = self.db.query(Room).filter_by(id=room_id).first()
        if not room:
            raise Exception("Phòng không tồn tại")
        rp = self.db.query(RoomPlayer).filter_by(room_id=room_id,user_id=user.id).first()
        if not rp:
            raise Exception("Không ở trong phòng")
        self.db.delete(rp)
        remaining = self.db.query(RoomPlayer).filter_by(room_id=room_id).count()
        if remaining <=1:
            room.status = "waiting"
        if remaining == 1:
            self.db.delete(room)
        self.db.commit()
    def _hash_pw(self, pw):
        if not pw:
            return None
        import bcrypt
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    def _verify_pw(self, pw, hash_pw):
        if not hash_pw:
            return True
        if not pw:
            return False
        import bcrypt
        return bcrypt.checkpw(pw.encode(), hash_pw.encode())

