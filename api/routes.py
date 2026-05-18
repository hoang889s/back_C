from flask import Blueprint, request, jsonify, g,session
from api.auth import login_required

from persistence.database import SessionLocal
from persistence.repository.roomrepository import RoomRepository
from persistence.repository.roomplayerrepository import RoomPlayerRepository

from services.game_manager import GameManager
from services.analyzer import Analyzer
from flask import Response

from core.utils.fen import fen_to_board, board_to_fen, get_start_fen
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
        # DOWNLOAD PGN
        # =============================
        @bp.route("/games/<int:game_id>/pgn", methods=["GET"])
        @login_required
        def download_pgn(game_id):
            db = get_db()
            try:
                gm = GameManager(db)
                game = gm.game_repo.get_game(game_id)

                if not game:
                    return jsonify({"error": "Game not found"}), 404
                
                # Generate PGN (use saved PGN or generate fresh)
                if game.pgn:
                    pgn_str = game.pgn
                else:
                    # Generate on-the-fly for games without saved PGN
                    from services.pgn_exporter import PGNExporter
                    exporter = PGNExporter()
            
                    white_name = game.white_player.username if game.white_player else "Unknown"
                    black_name = game.black_player.username if game.black_player else "AI"
                    pgn_str = exporter.export(game, white_name, black_name)
                
                return Response(
                    pgn_str,
                    mimetype="application/x-chess-pgn",
                    headers={
                        "Content-Disposition": f'attachment; filename="game_{game_id}.pgn"'
                    }
                )
            finally:
                db.close()
        # =============================
        # GET PGN
        # =============================
        @bp.route("/games/<int:game_id>/pgn/json", methods=["GET"])
        @login_required
        def get_pgn_json(game_id):
            db = get_db()
            try:
                gm = GameManager(db)
                game = gm.game_repo.get_game(game_id)

                if not game:
                    return jsonify({"error": "Game not found"}), 404
                
                if game.pgn:
                    pgn_str = game.pgn
                else:
                    from services.pgn_exporter import PGNExporter
                    exporter = PGNExporter()
                    white_name = game.white_player.username if game.white_player else "Unknown"
                    black_name = game.black_player.username if game.black_player else "AI"
                    pgn_str = exporter.export(game, white_name, black_name)
                
                return jsonify({
                    "status": "ok",
                    "game_id": game_id,
                    "pgn": pgn_str
                })
            finally:
                db.close()
        # =============================
        # REPLAY MATCH
        # =============================
        @bp.route("/games/<int:game_id>/replay", methods=["GET"])
        @login_required
        def replay_game(game_id):
            db = get_db()
            try:
                gm = GameManager(db)
                game = gm.game_repo.get_game(game_id)

                if not game:
                    return jsonify({"error": "Game not found"}), 404

                moves = gm.game_repo.get_moves(game_id)
                # Rebuild FEN state at each move
                board = fen_to_board(get_start_fen())
                replay_data = []

                replay_data.append({
                    "move_number": 0,
                    "move": None,
                    "san": None,
                    "fen": get_start_fen(),
                    "comment": "Starting position"
                })

                
                for move_model in moves:
                    parsed = gm._parse_move(move_model.move, move_model.promotion)
                    board.make_move(parsed)
                    fen = board_to_fen(board)

                    replay_data.append({
                        "move_number": move_model.move_number,
                        "move": move_model.move,
                        "san": move_model.san or move_model.move,
                        "fen": fen,
                        "player_id": move_model.player_id,
                        "timestamp": move_model.created_at.isoformat() if move_model.created_at else None,
                    })
                # Game metadata
                white_name = game.white_player.username if game.white_player else "Unknown"
                black_name = game.black_player.username if game.black_player else "AI"

                return jsonify({
                    "status": "ok",
                    "game": {
                        "id": game.id,
                        "white": {"id": game.white_player_id, "name": white_name},
                        "black": {"id": game.black_player_id, "name": black_name},
                        "result": game.status.value,
                        "end_reason": game.end_reason,
                        "created_at": game.created_at.isoformat() if game.created_at else None,
                        "ended_at": game.ended_at.isoformat() if game.ended_at else None,
                    },
                    "total_moves": len(moves),
                    "replay": replay_data,
                    "pgn": game.pgn,
                })
            finally:
                db.close()

                    
                


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