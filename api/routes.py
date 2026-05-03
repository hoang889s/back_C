from flask import Blueprint, request, jsonify, g,session
from api.auth import login_required

from persistence.database import SessionLocal
from persistence.repository.roomrepository import RoomRepository
from persistence.repository.roomplayerrepository import RoomPlayerRepository

from services.game_manager import GameManager
from services.analyzer import Analyzer
# =============================
# HELPER
# =============================
def get_db():
    return SessionLocal()
# =============================
# ROUTES
# =============================
class GameRoutes:
    def __init__(self):
        self.bp = Blueprint("game", __name__, url_prefix="/api/game")
        self._register_routes()
    def _register_routes(self):
        bp = self.bp
        # =============================
        # LOGOUT
        # =============================
        @bp.route("/logout", methods=["POST"])
        @login_required
        def logout():
            try:
                session.clear()
                return jsonify({
                    "status": "ok",
                    "message": "Logged out successfully"

                }),200
            except Exception as e:
                return jsonify({
                    "error": str(e)
                }),400
        # =============================
        # CREATE ROOM (REST ONLY)
        # =============================
        @bp.route("/rooms", methods=["POST"])
        @login_required
        def create_room():
            db = get_db()
            try:
                room_repo = RoomRepository(db)
                rp_repo = RoomPlayerRepository(db)
                data = request.get_json() or {}
                room = room_repo.create_room(
                    owner_id=g.user.id,
                    name=data.get("name", "Chess Room"),
                    mode=data.get("mode", "human"),
                )
                rp_repo.add_player(room.id, g.user.id)
                return jsonify({
                    "status": "ok",
                    "room": {
                        "code": room.code,
                        "name": room.name,
                        "mode": room.mode
                    }
                }),201
            except Exception as e:
                return jsonify({"error": str(e)}), 400
            finally:
                db.close()
        # =============================
        # LIST ROOMS
        # =============================
        @bp.route("/rooms", methods=["GET"])
        @login_required
        def list_rooms():
            db = get_db()
            try:
                room_repo = RoomRepository(db)
                rooms = room_repo.get_all()

                return jsonify({
                    "status": "ok",
                    "rooms": [
                        {
                            "code": r.code,
                            "name": r.name,
                            "mode": r.mode
                        } for r in rooms
                    ]
                })

            finally:
                db.close()
        # =============================
        # ROOM DETAIL
        # =============================
        @bp.route("/rooms/<room_code>", methods=["GET"])
        @login_required
        def get_room(room_code):
            db = get_db()
            try:
                room_repo = RoomRepository(db)
                rp_repo = RoomPlayerRepository(db)

                room = room_repo.get_by_code(room_code)
                if not room:
                    return jsonify({"error": "Room not found"}), 404

                players = rp_repo.get_players(room.id)

                return jsonify({
                    "status": "ok",
                    "room": {
                        "code": room.code,
                        "name": room.name,
                        "mode": room.mode,
                        "players": [p.username for p in players]
                    }
                })

            finally:
                db.close()
        # =============================
        # LOAD GAME STATE (READ ONLY)
        # =============================
        @bp.route("/games/<int:game_id>", methods=["GET"])
        @login_required
        def load_game(game_id):
            db = get_db()
            try:
                gm = GameManager(db)
                game = gm.game_repo.get_game(game_id)

                if not game:
                    return jsonify({"error": "Game not found"}), 404

                return jsonify({
                    "status": "ok",
                    "game": {
                        "id": game.id,
                        "fen": game.fen,
                        "turn": game.turn.value,
                        "status": game.status.value,
                        "white": game.white_player_id,
                        "black": game.black_player_id
                    }
                })

            finally:
                db.close()
        # =============================
        # GAME HISTORY
        # =============================
        @bp.route("/games/<int:game_id>/moves", methods=["GET"])
        @login_required
        def get_moves(game_id):
            db = get_db()
            try:
                gm = GameManager(db)
                moves = gm.game_repo.get_moves(game_id)

                return jsonify({
                    "status": "ok",
                    "moves": [
                        {
                            "move": m.move,
                            "player": m.player_id
                        } for m in moves
                    ]
                })

            finally:
                db.close()
# =============================
# EXPORT
# =============================
_game_routes = GameRoutes()
game_bp = _game_routes.bp