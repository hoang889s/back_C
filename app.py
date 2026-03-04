from flask import Flask, request, jsonify
from flask_cors import CORS
from board import Board
from minimax import Minimax
from constants import WHITE, BLACK
from typing import Optional
import logging
class Config:
    HOST = "127.0.0.1"
    PORT = 8000
    DEBUG = True
    AI_DEPTH = 4
    AI_COLOR = BLACK
class GameManager:
    # Quản lý trạng thái game board + ai
    # khởi tạo
    def __init__(self,ai_depth:int=Config.AI_DEPTH,ai_color=Config.AI_COLOR):
        self.board = Board()
        self.ai = Minimax(depth=ai_depth)
        self.ai_color = ai_color
        self.logger = logging.getLogger(self.__class__.__name__)
    # trả về trạng thái bàn cờ
    def get_board_state(self) -> list:
        return self.board.board
    # hàm duyệt nước đi người chơi
    def apply_player_move(self, move: tuple) -> bool:
        try:
            self.board.make_move(move)
            return True
        except Exception as e:
            self.logger.error(f"Nước đi không hợp lệ {move}: {e}")
            return False
    # hàm máy đánh 
    def compute_ai_move(self) -> Optional[tuple]:
        move = self.ai.find_best_move(self.board, self.ai_color)
        if move:
            self.board.make_move(move)
            self.logger.info(f"AI đánh: {move}")
        return move
    # hàm reset
    def reset(self):
        self.board = Board()
        self.logger.info("Bàn cờ đã reset")
# khu vực định nghĩa endpoint api,routes
class GameRoutes:
    # khởi tạo
    def __init__(self, game: GameManager):
        self.game   = game
        self.logger = logging.getLogger(self.__class__.__name__)
    # GET/board trả về bàn cờ 8x8
    def get_board(self):
        return jsonify(self.game.get_board_state())
    # POST /move tạo và gửi các nước đi về server
    # Body: { "from": {"row": 6, "col": 4}, "to": {"row": 4, "col": 4} }
    # Response: { "status": "ok"|"invalid", "board": [[...]] }
    def player_move(self):
        # validate input nếu không đáp ứng đúng sẽ trả về badrequest
        # ở body của phần api gừi về phải có from và to
        data = request.get_json(silent=True)
        if not data or "from" not in data or "to" not in data:
            return jsonify({
                "status": "error",
                "message": "Body phải có 'from' và 'to'"
            }), 400
        from_sq = data["from"]
        to_sq = data["to"]
        # from và to phải khớp với row và col không sẽ trả về badrequest
        if not all(k in from_sq for k in ("row", "col")) or \
           not all(k in to_sq   for k in ("row", "col")):
            return jsonify({
                "status": "error",
                "message": "'from' và 'to' phải có 'row' và 'col'"
            }), 400
        # người chơi đánh
        move = (from_sq["row"], from_sq["col"], to_sq["row"], to_sq["col"])
        success = self.game.apply_player_move(move)
        # nếu không đúng sẽ trả về lỗi 422 Unprocessable Entity(dư liệu có trả về nhưng không đúng định dạng)
        if not success:
            return jsonify({
                "status":  "invalid",
                "message": "Nước đi không hợp lệ",
                "board":   self.game.get_board_state(),   # trả board để UI đồng bộ
            }), 422
        # ai phản hồi lại
        ai_move = self.game.compute_ai_move()
        ai_move_json = None
        if ai_move:
            ai_move_json = {
                "from": {"row": ai_move[0], "col": ai_move[1]},
                "to":   {"row": ai_move[2], "col": ai_move[3]},
            }
        # trả về dữ liệu json trạng thái 200 thành công
        return jsonify({
            "status":  "ok",
            "ai_move": ai_move_json,
            "board":   self.game.get_board_state(),
        }), 200
        # Post / gửi đi để reset lại
    def reset(self):
        self.game.reset()
        return jsonify({
            "status":  "ok",
            "message": "Game đã được reset",
            "board":   self.game.get_board_state(),
        }), 200
# đăng ký routes và chạy chính
class ChessApp:
    # khởi tạo
    def __init__(self, config: type = Config):
        self.config = config
        self.app    = Flask(__name__)
        self._setup_logging()
        self._setup_cors()
        self._setup_routes()
    # cài logging
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG if self.config.DEBUG else logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    # cài cors cho phép bên khác gọi
    def _setup_cors(self):
        CORS(self.app)
    # cài routes
    def _setup_routes(self):
        game   = GameManager(ai_depth=self.config.AI_DEPTH, ai_color=self.config.AI_COLOR)
        routes = GameRoutes(game)

        self.app.add_url_rule("/board", "get_board",    routes.get_board,    methods=["GET"])
        self.app.add_url_rule("/move",  "player_move",  routes.player_move,  methods=["POST"])
        self.app.add_url_rule("/reset", "reset_game",   routes.reset,        methods=["POST"])
    def run(self):
        self.logger.info(f"Server chạy tại http://{self.config.HOST}:{self.config.PORT}")
        self.app.run(
            host=self.config.HOST,
            port=self.config.PORT,
            debug=self.config.DEBUG,
        )

if __name__ == "__main__":
    ChessApp(config=Config).run()



