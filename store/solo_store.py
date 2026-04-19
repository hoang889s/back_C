from manager.game_manager import GameManager
from threading import Lock
from datetime import datetime
class SoloStore:
    def __init__(self):
        self.games = {}
        self.lock = Lock()
    # lấy hoặc tạo game
    def get_or_create(self,user_id):
        with self.lock:
            if user_id not in self.games:
                self.games[user_id] = {
                    "game":GameManager(),
                    "last_access": datetime.utcnow()
                }
            self.games[user_id]["last_access"] = datetime.utcnow()
            return self.games[user_id]["game"]
    # lấy game
    def get(self,user_id):
        with self.lock:
            data = self.games.get(user_id)
            if not data:
                return None
            data["last_access"] = datetime.utcnow()
            return data["game"]
    def reset(self,user_id):
        with self.lock:
            self.games[user_id] = {
                "game": GameManager(),
                "last_access": datetime.utcnow()
            }
    # xóa
    def delete(self,user_id):
        with self.lock:
            if user_id in self.games:
                del self.games[user_id]
    # dọn dẹp
    def cleanup_inactive(self, timeout_seconds=3600):
        now = datetime.utcnow()
        with self.lock:
            to_delete = []
            for user_id, data in self.games.items():
                last = data["last_access"]
                if (now - last).total_seconds() > timeout_seconds:
                    to_delete.append(user_id)
            for user_id in to_delete:
                del self.games[user_id]
    # debug
    def stats(self):
        with self.lock:
            return {
                "total_games": len(self.games),
                "users": list(self.games.keys())
            }
