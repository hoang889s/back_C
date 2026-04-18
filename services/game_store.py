from services.game_manager import GameManager
class GameStore:
    def __init__(self):
        self.games = {}
    def get_game(self, user_id):
        if user_id not in self.games:
            self.games[user_id] = GameManager()
        return self.games[user_id]
    def reset_game(self, user_id):
        if user_id in self.games:
            self.games[user_id].reset()

