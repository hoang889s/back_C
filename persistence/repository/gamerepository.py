from persistence.models import Game, Move,Turn,GameResult
from persistence.repository.baserepository import BaseRepository
from core.utils.fen import get_start_fen
class GameRepository(BaseRepository):
    # tao game ok
    def create_game(self, room_id, white_id, black_id=None,ai_difficulty=None):
        game = Game(
            room_id=room_id,
            white_player_id=white_id,
            black_player_id=black_id,
            turn=Turn.WHITE,
            status=GameResult.ONGOING,
            fen=get_start_fen(),
            ai_difficulty=ai_difficulty,
        )
        self.add(game)
        self.commit()
        self.refresh(game)
        return game
    # get game ok
    def get_game(self, game_id):
        return self.db.query(Game).filter(Game.id == game_id).first()
    # get by room id
    def get_by_room_id(self, room_id):
        return self.db.query(Game).filter(Game.room_id == room_id).first()
    # add move ok
    def add_move(self, game_id, move_str, player_id, move_number,promotion=None):
        game = self.get_game(game_id)
        if not game:
            return None
        move_number = len(game.moves) + 1
        mv = Move(
            game_id=game_id,
            move=move_str,
            player_id=player_id,
            move_number=move_number,
            promotion=promotion
        )
        self.db.add(mv)
        self.db.flush()
        #self.commit()
        return mv
    # update game ok
    def update_game_state(self, game_id, fen=None, turn=None, status=None):
        game = self.get_game(game_id)
        if not game:
            return None
        if fen is not None:
            game.fen = fen
        if turn is not None:
            game.turn = turn
        if status is not None:
            game.status = status
        self.commit()
        return game
    # assign black player ok
    def assign_black_player(self, game_id, user_id):
        game = self.get_game(game_id)
        if not game:
            return None
        if not game.black_player_id:
            game.black_player_id = user_id
            self.commit()
        return game
    # get moves
    def get_moves(self, game_id):
        game = self.get_game(game_id)
        if not game:
            return []
        return game.moves
