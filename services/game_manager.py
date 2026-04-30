from core.board import Board
from core.constants import WHITE, BLACK
from persistence.repository.gamerepository import GameRepository
from persistence.repository.roomplayerrepository import RoomPlayerRepository
from persistence.repository.roomrepository import RoomRepository
from persistence.repository.userepository import UserRepository
from persistence.models import Move
class GameManager:
    def __init__(self, db):
        self.db = db
        self.games = {}
        self.game_repo = GameRepository(db)
        self.room_repo = RoomRepository(db)
        self.room_player_repo = RoomPlayerRepository(db)
        self.user_repo = UserRepository(db)
    # tạo phòng
    def create_game(self, room_code):
        room = self.room_repo.get_by_code(room_code)
        if not room:
            raise Exception("Room not found")
        players = self.room_player_repo.get_players(room.id)
        if len(players) < 1:
            raise Exception("Not enough players")
        white_id = players[0].user_id
        black_id = players[1].user_id if len(players) > 1 else None
        game = self.game_repo.create_game(
            room_id=room.id,
            white_id=white_id,
            black_id=black_id
        )
        board = Board()
        self.games[game.id] = {
            "board": board,
            "turn": WHITE,
            "room_id": room.id
        }
        return game


    # tải game từ database ok
    def load_game(self,game_id):
        if game_id in self.games:
            return self.games[game_id]
        game_model = self.game_repo.get_game(game_id)
        if not game_model:
            raise Exception("Game not found")
        board = Board()
        moves = (
            self.db.query(Move)
            .filter(Move.game_id == game_id)
            .order_by(Move.move_number)
            .all()
        )
        for mv in moves:
            parsed = self._parse_move(mv.move)
            board.make_move(parsed)
        game = {
            "board": board,
            "turn": board.turn,
            "room_id": game_model.room_id
        }
        # cache lại
        self.games[game_id] = game
        # load players
        room_players = self.room_player_repo.get_players(game_model.room_id)
        game["players"] = [p.user_id for p in room_players]
        return game

    # di chuyển ok
    def make_move(self, game_id, move_str, player_id):
        game = self.load_game(game_id)
        board = game["board"]
        move = self._parse_move(move_str)
        # validate turn
        if player_id not in game.get("players", []):
            raise Exception("Player not in game")
        # validate move
        legal_moves = board.generate_all_legal_moves(board.turn)
        if move not in legal_moves:
            raise Exception("Invalid move")
        board.make_move(move)
        return {
            "move": move_str,
            "turn": board.turn,
            "is_check": board.is_in_check(board.turn),
            "is_checkmate": board.is_checkmate(board.turn),
        }
    # AI move
    def ai_move(self,game_id,analyzer):
        game = self.load_game(game_id)
        board = game["board"]
        result = analyzer.analyze(board, board.turn)
        move_str = result["best_move"]
        move = self._parse_move(move_str)
        board.make_move(move)
        return {
            **result,
            "move": move_str,
            "turn": board.turn,
            "is_check": board.is_in_check(board.turn),
            "is_checkmate": board.is_checkmate(board.turn),
        }
    def _parse_move(self, move_str):
        def to_index(sq):
            col = ord(sq[0]) - ord('a')
            row = 8 - int(sq[1])
            return row, col
        fr = to_index(move_str[:2])
        to = to_index(move_str[2:4])
        return (fr[0], fr[1], to[0], to[1])

