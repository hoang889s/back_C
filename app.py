# Flask tạo web server
# request phản hồi
# CORS cho phép React lấy dữ liệu
# jsonify trả về dữ liệu json
from flask import Flask, request, jsonify
from flask_cors import CORS
from board import Board
from minimax import Minimax
from constants import WHITE, BLACK, EMPTY
from typing import Optional
import logging
class Config:
    # Thông tin cấu hình của server
    HOST = "127.0.0.1"
    PORT = 8000
    DEBUG = True
    AI_DEPTH = 4
    AI_COLOR = BLACK
class GameManager:
    # Quản lý các trạng của game
    # hàm khởi tạo đổi tượng quản lý
    def __init__(self,ai_depth:int = Config.AI_DEPTH,ai_color=Config.AI_COLOR):
        self.board = Board()
        self.ai = Minimax(depth=ai_depth)
        self.ai_color = ai_color
        self.logger = logging.getLogger(self.__class__.__name__)
    # hàm trả về dữ liệu bàn cờ
    # trả về bàn cờ 8x8
    def get_board_state(self)->list:
        return self.board.board
    # người chơi đánh
    def apply_player_move(self,move:tuple)->bool:
        try:
            self.board.make_move(move)
            return True
        except Exception as e:
            self.logger.error(f"Lỗi khi thực hiện nước đi {move}: {e}")
            return False
    # ai đánh
    def compute_ai_move(self) -> Optional[tuple]:
        move = self.ai.find_best_move(self.board,self.ai_color)
        if move:
            self.board.make_move(move)
            self.logger.info(f"AI đánh :{move}")
        return move
    # trạng thái reset
    def reset(self):
        self.board = Board()
        self.logger.info("Bàn cờ đã reset")
# xây dựng các phương thức Routes tách Flask ra khỏi Routes dễ mở rộng
class GameRoutes:
    # khởi tạo
    def __init__(self,game:GameManager):
        self.game = game
        self.logger = logging.getLogger(self.__class__.__name__)
    # frontend sẽ gọi và hiện thị bàn cờ
    def get_board(self):
        return jsonify(self.game.get_board_state())
    # frontend nhận nước đi của người chơi
    def player_move(self):
        data = request.get_json()
        if not data or "move" not in data:
            return jsonify({"status": "error", "message": "Thiếu dữ liệu 'move'"}),400
        move = tuple(data["move"])
        success = self.game.apply_player_move(move)
        if success:
            return jsonify({"status":"ok"}),200
        return jsonify({"status":"error","message":"Nước đi không hợp lệ"}),422
    # frontend sẽ gọi nước đi từ server của ai
    def ai_move(self):
        move = self.game.compute_ai_move()
        return jsonify({"move":list(move) if move else None })
    def reset(self):
    # reset game
        self.game.reset()
        return jsonify({"status": "ok", "message": "Game đã được reset"}),200
# khu vực bọc flask
class ChessApp:
    def __init__(self,config:type = Config):
        self.config = config
        self.app = Flask(__name__)
        self._setup_logging()
        self._setup_cors()
        self._setup_routes()
    # cho phép React gọi từ localhost:5173
    def _setup_logging(self):
        logging.basicConfig(level=logging.DEBUG if self.config.DEBUG else logging.INFO, format="%(asctime)s [%(levelname)s]:%(message)s")
        self.logger = logging.getLogger(self.__class__.__name__)
    def _setup_cors(self):
        CORS(self.app)
    def _setup_routes(self):
        game = GameManager(ai_depth=self.config.AI_DEPTH,ai_color=self.config.AI_COLOR)
        routes = GameRoutes(game)
        # đăng ký routes (api)
        self.app.add_url_rule("/board","get_board",routes.get_board,methods=["GET"])
        self.app.add_url_rule("/move", "player_move",routes.player_move,methods=["POST"])
        self.app.add_url_rule("/ai_move","ai_move",routes.ai_move,methods=["GET"])
        self.app.add_url_rule("/reset","reset_game",routes.reset,methods=["POST"])
    def run(self):
        self.logger.info(f"Server đang chạy tại http://{self.config.HOST}:{self.config.PORT}")
        self.app.run(
            host =self.config.HOST,
            port=self.config.PORT,
            debug=self.config.DEBUG
        )
if __name__ == "__main__":
    chess_app = ChessApp(config=Config)
    chess_app.run()
    
        


