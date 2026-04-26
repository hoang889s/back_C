from persistence.models import Game, Move
from persistence.repository.baserepository import BaseRepository
class GameRepository(BaseRepository):
    def create_game(self, room_id, white_id, black_id=None):
        game = Game(
            room_id=room_id,
            white_player_id=white_id,
            black_player_id=black_id
        )
        self.add(game)
        self.commit()
        self.refresh(game)
        return game
    def get_game(self, game_id):
        return self.db.query(Game).filter(Game.id == game_id).first()
    def add_move(self, game_id, move, player_id, move_number):
        mv = Move(
            game_id=game_id,
            move=move,
            player_id=player_id,
            move_number=move_number
        )
        self.add(mv)
        self.commit()
        return mv