from board import Board
from constants import WHITE, BLACK
from threading import Lock
# khả năng diễn ra của một trận đấu
class Room:
    def __init__(self,room_code):
        self.room_code = room_code
        self.board = Board()
        self.players = []
        self.lock = Lock()
    # quản lý người chơi
    def add_player(self,user_id):
        if len(self.players)>=2:
            return False
        if len(self.players) == 0:
            color = WHITE
        else:
            color = BLACK
        self.players.append({"id":user_id,"color":color})
        return color
    def remove_player(self,user_id):
        self.players = [p for p in self.players if p["id"] != user_id]
    def get_player_color(self, user_id):
        for p in self.players:
            if p["id"] == user_id:
                return p["color"]
        return None
    def get_current_player(self):
        for p in self.players:
            if p["color"] == self.board.turn:
                return p["id"]
        return None
    def is_full(self):
        return len(self.players) == 2
    # logic game
    def make_move(self,user_id,move):
        with self.lock:
            color = self.get_player_color(user_id)
            if color is None:
                return {"error": "Người chơi  không ở trong phòng"}
            if color != self.board.turn:
                return {"error": "Không phải lượt của bạn"}
            fr, fc, tr, tc = move[:4]
            legal_moves = self.board.generate_legal_moves(fr, fc)
            if move not in legal_moves:
                return {"error": "Invalid move"}
            self.board.make_move(move)
            return {
                "success": True,
                "board": self.board.board,
                "turn": self.board.turn
            }
# quản lý phòng
class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.lock = Lock()
    def create_room(self, room_code):
        with self.lock:
            if room_code in self.rooms:
                return None
            room = Room(room_code)
            self.rooms[room_code] = room
            return room
    def get_room(self,room_code):
        return self.rooms.get(room_code)

    def delete_room(self,room_code):
        with self.lock:
            if room_code in self.rooms:
                del self.rooms[room_code]
    
    def join_room(self,room_code,user_id):
        room = self.get_room(room_code)
        if not room:
            return {"error": "không tìm thấy phòng"}
        color = room.add_player(user_id)
        if not color:
            return {"error": "Phòng đầy"}
        return {
            "success": True,
            "color": color
        }
    def leave_room(self, room_code, user_id):
        room = self.get_room(room_code)
        if not room:
            return
        room.remove_player(user_id)
        if len(room.players) == 0:
            self.delete_room(room_code)
room_manager = RoomManager()

    
