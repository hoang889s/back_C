from flask import Blueprint, request, jsonify, g
from api.auth import login_required
from extensions import socketio
#from sockets import socketio  # để emit realtime

from persistence.database import SessionLocal
from services.game_manager import GameManager
from services.analyzer import Analyzer
def get_services():
    db = SessionLocal()
    gm = GameManager(db)
    analyzer = Analyzer(depth=4)
    return db, gm, analyzer
class GameRoutes:
    def __init__(self):
        self.bp = Blueprint("game", __name__, url_prefix="/game")
        self._register_routes()

    def _register_routes(self):
        bp = self.bp

        # =============================
        # CREATE GAME
        # =============================
        @bp.route("/create", methods=["POST"])
        @login_required
        def create_game():
            db, gm, _ = get_services()
            try:
                data = request.get_json(silent=True) or {}
                room_code = data.get("room_code")

                game = gm.create_game(room_code)

                socketio.emit("game_created", {
                    "game_id": game.id
                }, room=room_code)

                return jsonify({
                    "status": "ok",
                    "game_id": game.id,
                }), 200

            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 400

            finally:
                db.close()

        # =============================
        # LOAD GAME
        # =============================
        @bp.route("/<int:game_id>", methods=["GET"])
        @login_required
        def load_game(game_id):
            db, gm, _ = get_services()
            try:
                game = gm.load_game(game_id)

                return jsonify({
                    "status": "ok",
                    "board": game["board"].board,
                    "turn": game["turn"]
                }), 200

            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 404

            finally:
                db.close()

        # =============================
        # MOVE
        # =============================
        @bp.route("/<int:game_id>/move", methods=["POST"])
        @login_required
        def make_move(game_id):
            db, gm, _ = get_services()
            try:
                data = request.get_json(silent=True) or {}
                move = data.get("move")

                result = gm.make_move(
                    game_id=game_id,
                    move_str=move,
                    player_id=g.user.id
                )

                game = gm.load_game(game_id)
                room_id = game.get("room_id")

                socketio.emit("move_made", {
                    "move": move,
                    "board": result["board"],
                    "turn": result["turn"],
                    "check": result["is_check"],
                    "checkmate": result["is_checkmate"]
                }, room=room_id)

                return jsonify({
                    "status": "ok",
                    **result
                }), 200

            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 400

            finally:
                db.close()

        # =============================
        # AI MOVE
        # =============================
        @bp.route("/<int:game_id>/ai", methods=["POST"])
        @login_required
        def ai_move(game_id):
            db, gm, analyzer = get_services()
            try:
                result = gm.ai_move(
                    game_id=game_id,
                    analyzer=analyzer
                )

                game = gm.load_game(game_id)
                room_id = game.get("room_id")

                socketio.emit("ai_move", result, room=room_id)

                return jsonify({
                    "status": "ok",
                    **result
                }), 200

            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 400

            finally:
                db.close()

        # =============================
        # ANALYZE
        # =============================
        @bp.route("/<int:game_id>/analyze", methods=["GET"])
        @login_required
        def analyze(game_id):
            db, gm, analyzer = get_services()
            try:
                game = gm.load_game(game_id)
                board = game["board"]

                result = analyzer.analyze(board, board.turn)

                return jsonify({
                    "status": "ok",
                    **result
                }), 200

            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 400

            finally:
                db.close()


# export blueprint
_game_routes = GameRoutes()
game_bp = _game_routes.bp