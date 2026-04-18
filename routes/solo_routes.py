from flask import Blueprint, request, jsonify
from constants import WHITE, BLACK, EMPTY
from services.game_store import GameStore
bp = Blueprint("solo", __name__)
store = GameStore()
def get_user_game():
    user_id = request.headers.get("X-User-Id", "guest")
    return store.get_game(user_id)
@bp.route("/board", methods=["GET"])
def get_board():
    game = get_user_game()

    color = game.board.turn
    status = game.get_game_status(color)
    return jsonify({
        "board": game.get_board_state(),
        "turn": "white" if color == WHITE else "black",
        "game_status":status,
    })
@bp.route("/legal-moves", methods=["GET"])
def legal_moves():
    game = get_user_game()
    try:
        row = int(request.args.get("row", -1))
        col = int(request.args.get("col", -1))
    except ValueError:
        return jsonify({"error": "row/col phải là số"}), 400
    if not (0 <= row < 8 and 0 <= col < 8):
        return jsonify({"error": "row/col ngoài phạm vi"}), 400
    moves = game.get_legal_moves_for(row, col)
    return jsonify({
        "moves":moves
    })
@bp.route("/move", methods=["POST"])
def move():
    game = get_user_game()
    data = request.get_json(silent=True) or {}
    try:
        from_sq = data["from"]
        to_sq = data["to"]
        move =(
            from_sq["row"], from_sq["col"],
            to_sq["row"], to_sq["col"]
        )
    except Exception:
        return jsonify({"error": "Dữ liệu không hợp lệ"}), 400
    success = game.apply_player_move(move)
    if not success:
        return jsonify({
            "status": "invalid",
            "board": game.get_board_state()
        }),422
    ai_move = None
    if game.board.turn == game.ai_color:
        ai_move = game.compute_ai_move()
    color = game.board.turn
    status = game.get_game_status(color)
    return jsonify({
        "status": "ok",
        "board": game.get_board_state(),
        "turn": "white" if color == WHITE else "black",
        "game_status": status,
        "ai_move": ai_move
    })
@bp.route("/reset", methods=["POST"])
def reset():
    game = get_user_game()
    game.reset()
    return jsonify({
        "board": game.get_board_state(),
        "turn": "white",
        "game_status": {"state": "ongoing"}
    })
