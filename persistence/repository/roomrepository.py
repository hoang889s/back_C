from persistence.models import Room, RoomPlayer
from persistence.repository.baserepository import BaseRepository
class RoomRepository(BaseRepository):
    def create_room(self,**kwargs):
        room = Room(**kwargs)
        self.add(room)
        self.commit()
        self.refresh(room)
        return room
    def get_by_code(self, code: str):
        return self.db.query(Room).filter(Room.code == code).first()
    def list_rooms(self):
        return self.db.query(Room).all()
