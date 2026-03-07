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
    # hàm trả về trạng thái quân sau mỗi nước đi
    def get_game_status(self,color):
        # nếu chiếu hết
        if self.board.is_checkmate(color):
            # trả về dictionary
            return {"state":"checkmate","loser":"white" if color==WHITE else "black"}
        # nếu hòa cờ
        if self.board.is_stalemate(color):
            return {"state":"stalemate"}
        # nếu là chiếu tướng
        if self.board.is_in_check(color):
            return {"state":"check","color":"white" if color==WHITE else "black"}
        # vẫn tiếp tục bình thường
        return {"state":"ongoing"}
    # hàm trả về danh sách nước đi hợp lệ tại row và col
    def get_legal_moves_for(self,row:int,col:int)->list:
        # lấy vị trí quân cờ hiện tại
        piece = self.board.get_piece(row,col)
        # nếu là ô cờ trống
        if piece == '.':
            return []
        raw_moves = self.board.generate_legal_moves(row,col)
        # chuyển dạng [{"row": tr, "col": tc}, ...]
        return [{"row":m[2],"col":m[3]} for m in raw_moves]
    # hàm duyệt nước đi người chơi
    def apply_player_move(self, move: tuple) -> bool:
        try:
            # lấy tọa độ đầu và cuối của một nước đi
            fr,fc,tr,tc = move[0],move[1],move[2],move[3]
            legal_moves = self.board.generate_legal_moves(fr,fc)
            # so khơp với mathched
            matched = [m for m in legal_moves if m[2] == tr and m[3] == tc]
            if not matched:
                return False
            
            self.board.make_move(matched[0])
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
        # áp dụng màu quân
        color = self.game.board.turn # trắng hoặc đen
        # trạng thái
        status = self.game.get_game_status(color)
        return jsonify({
            "board":self.game.get_board_state(),
            "turn":"white" if color == WHITE else "black",
            "game_status":status,
        })
    # GET /legal-moves?row=6&col=4 → nước đi hợp lệ cho quân tại ô đó
    def legal_moves(self):
        # trường hợp thành công
        try:
            row = int(request.args.get("row",-1))
            col = int(request.args.get("col",-1))
        # nhảy vào các lỗi
        except ValueError:
            return jsonify({"status":"error","message":"row và col phải là số nguyên"}),400
        if not (0<=row<8 and 0 <= col < 8):
            return jsonify({"status":"error","message":"row/col phải trong [0, 7]"}),400
        moves = self.game.get_legal_moves_for(row,col)
        return jsonify({"status":"ok","moves":moves})
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
        # Sau khi người chơi đi → kiểm tra trạng thái bên đen (AI)
        ai_color_str = "black" if self.game.ai_color == BLACK else "white"
        post_player_status = self.game.get_game_status(self.game.ai_color)
        
        post_ai_status = None
        ai_move_json = None
        if post_player_status["state"] == "ongoing" or post_player_status["state"] == "check":
            ai_move = self.game.compute_ai_move()
            if ai_move:
                ai_move_json = {
                    "from": {"row": ai_move[0], "col": ai_move[1]},
                    "to":   {"row": ai_move[2], "col": ai_move[3]},
                }
                # Sau khi AI đi → kiểm tra trạng thái bên người chơi (WHITE)
                post_ai_status = self.game.get_game_status(WHITE)
        # Xác định trạng thái cuối để trả về frontend
        final_status = post_ai_status if post_ai_status else post_player_status

        # trả về dữ liệu json trạng thái 200 thành công
        return jsonify({
            "status":  "ok",
            "ai_move": ai_move_json,
            "board":   self.game.get_board_state(),
            "turn":"white" if self.game.board.turn == WHITE else "black",
            "game_status":final_status,
        }), 200
        # Post / gửi đi để reset lại
    def reset(self):
        self.game.reset()
        return jsonify({
            "status":  "ok",
            "message": "Game đã được reset",
            "board":   self.game.get_board_state(),
            "turn":"white",
            "game_status":{"state":"ongoing"},
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
        self.app.add_url_rule("/legal-moves","legal_moves",routes.legal_moves,methods=["GET"])
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



