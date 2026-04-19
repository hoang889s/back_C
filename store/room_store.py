from threading import Lock
from manager.game_manager import GameManager
class RoomStore:
    def __init__(self):
        self.rooms = {}
        self.lock = Lock()
    def create_room(self, room_id):
        with self.lock:
            if room_id not in self.rooms:
                self.rooms[room_id] = {
                    "game": GameManager(),
                    "players": [],
                }
        return self.rooms[room_id]
    # lấy phòng
    def get_room(self,room_id):
        return self.rooms.get(room_id)
    # vào phòng
    def join_room(self, room_id, user_id):
        room = self.create_room(room_id)
        # check full
        if len(room["players"]) >= 2:
            raise Exception("Phòng đầy")
        # tránh trùng phòng
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
    # loại người chơi
    def remove_player(self, room_id, user_id):
        with self.lock:
            room = self.rooms.get(room_id)
            if not room:
                return
            room["players"] = [
                p for p in room["players"] if p["user_id"] != user_id
            ]
        # nếu không còn ai xóa phòng
        if len(room["players"]) == 0:
            del self.rooms[room_id]
    # game
    def get_game(self, room_id):
        room = self.get_room(room_id)
        return room["game"] if room else None
    # make move
    def make_move(self, room_id, move):
        room = self.get_room(room_id)
        if not room:
            return None
        game = room["game"]
        return {
            "board": game.get_board_state(),
            "turn": game.board.turn,
            "players": room["players"]
        }
    # reset room
    def reset_room(self, room_id):
        with self.lock:
            room = self.get_room(room_id)
            if not room:
                return None
            room["game"] = GameManager()
            return {
                "board": room["game"].get_board_state(),
                "turn": room["game"].board.turn,
                "players": room["players"]
            }
    # debug
    def stats(self):
        with self.lock:
            return{
                "total_rooms": len(self.rooms),
                "rooms":{
                    room_id:{
                        "players": room["players"]
                    }
                    for room_id, room in self.rooms.items()
                }
            }
            
