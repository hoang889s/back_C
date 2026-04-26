from persistence.models import RoomPlayer
from persistence.repository.baserepository import BaseRepository
class RoomPlayerRepository(BaseRepository):
    def add_player(self, room_id, user_id):
        rp = RoomPlayer(room_id=room_id, user_id=user_id)
        self.add(rp)
        self.commit()
        return rp
    def get_players(self, room_id):
        return self.db.query(RoomPlayer).filter(
            RoomPlayer.room_id == room_id
        ).all()
