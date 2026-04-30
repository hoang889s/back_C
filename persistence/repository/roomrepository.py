import random
import string

from persistence.models import Room, RoomStatus, GameMode
from persistence.repository.baserepository import BaseRepository
class RoomRepository(BaseRepository):
    # PRIVATE: generate room code
    def _generate_code(self, length=6):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            exists = self.db.query(Room).filter(Room.code == code).first()
            if not exists:
                return code
    # CREATE ROOM
    def create_room(
        self,
        owner_id: int,
        name: str = "Chess Room",
        mode: GameMode = GameMode.HUMAN,
        is_private: bool = False,
        password_hash: str = None,
        time_limit: int = 600
):
        room = Room(
            name=name,
            code=self._generate_code(),
            owner_id=owner_id,
            mode=mode,
            is_private=is_private,
            password_hash=password_hash,
            time_limit=time_limit,
            status=RoomStatus.WAITING
        )
        self.add(room)
        self.commit()
        self.refresh(room)
        return room
    # GET BY CODE
    def get_by_code(self, code: str):
        return self.db.query(Room).filter(Room.code == code).first()
    # GET BY ID
    def get_by_id(self, room_id: int):
        return self.db.query(Room).filter(Room.id == room_id).first()
    # LIST ROOMS
    def list_rooms(self, status: RoomStatus = None):
        query = self.db.query(Room)
        if status:
            query = query.filter(Room.status == status)
        return query.all()
    # DELETE ROOM
    def delete_room(self, room_id: int):
        room = self.get_by_id(room_id)
        if not room:
            return False
        self.db.delete(room)
        self.commit()
        return True
        
