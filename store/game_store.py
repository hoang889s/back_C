from manager.game_manager import GameManager
from threading import Lock

class GameStore:
    def __init__(self):
        self.rooms = {}  # room_id -> game data
        self.lock = Lock()

    def create_room(self, room_id):
        with self.lock:
            if room_id not in self.rooms:
                self.rooms[room_id] = {
                    "game": GameManager(),
                    "players": [],   # [{user_id, color}]
                }
        return self.rooms[room_id]

    def get_room(self, room_id):
        return self.rooms.get(room_id)

    def add_player(self, room_id, user_id):
        with self.lock:
            room = self.create_room(room_id)

            # tránh add trùng
            for p in room["players"]:
                if p["user_id"] == user_id:
                    return room

            # gán màu
            color = "white" if len(room["players"]) == 0 else "black"

            room["players"].append({
                "user_id": user_id,
                "color": color
            })

            return room

    def remove_player(self, room_id, user_id):
        with self.lock:
            room = self.rooms.get(room_id)
            if not room:
                return

            room["players"] = [
                p for p in room["players"] if p["user_id"] != user_id
            ]

            # nếu phòng rỗng → xóa luôn
            if len(room["players"]) == 0:
                del self.rooms[room_id]

    def get_game(self, room_id):
        room = self.get_room(room_id)
        return room["game"] if room else None

    def make_move(self, room_id, move):
        room = self.get_room(room_id)
        if not room:
            raise Exception("Room không tồn tại")

        game = room["game"]
        game.make_move(move)

        return {
            "board": game.get_board_state(),
            "turn": game.board.turn
        }

    def get_state(self, room_id):
        room = self.get_room(room_id)
        if not room:
            return None

        game = room["game"]

        return {
            "board": game.get_board_state(),
            "turn": game.board.turn,
            "players": room["players"]
        }