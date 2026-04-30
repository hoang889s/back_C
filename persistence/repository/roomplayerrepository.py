from persistence.models import RoomPlayer
from persistence.repository.baserepository import BaseRepository
from sqlalchemy.exc import IntegrityError
class RoomPlayerRepository(BaseRepository):
    def add_player(self, room_id, user_id,role ="player"):
        # check user đã trong room chưa
        existing = self.db.query(RoomPlayer).filter(
            RoomPlayer.room_id == room_id,
            RoomPlayer.user_id == user_id
        ).first()
        if existing:
            return existing
        rp = RoomPlayer(
            room_id=room_id,
            user_id=user_id,
            role=role
        )
        self.add(rp)
        try:
            self.commit()
        except IntegrityError:
            self.rollback()
            raise Exception("Failed to add player (duplicate or constraint error)")
        
        return rp
    def get_players(self, room_id):
        return self.db.query(RoomPlayer).filter(
            RoomPlayer.room_id == room_id
        ).all()
    def count_players(self, room_id):
        return self.db.query(RoomPlayer).filter(
            RoomPlayer.room_id == room_id
        ).count()
    def is_in_room(self, room_id, user_id):
        return self.db.query(RoomPlayer).filter(
            RoomPlayer.room_id == room_id,
            RoomPlayer.user_id == user_id
        ).first() is not None
    def remove_player(self, room_id, user_id):
        player = self.db.query(RoomPlayer).filter(
            RoomPlayer.room_id == room_id,
            RoomPlayer.user_id == user_id
        ).first()
        if player:
            self.db.delete(player)
            self.commit()
            return True
        return False
