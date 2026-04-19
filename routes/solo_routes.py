from flask import Blueprint, request, jsonify
from store.solo_store import SoloStore
from constants import WHITE,BLACK
bp = Blueprint("solo", __name__)
store = SoloStore()
def get_user_id():
    uid = request.headers.get("X-User-Id")
    if not uid:
        uid = f"guest-{request.remote_addr}"
    return uid
# lấy game
def get_game():
    return store.get_or_create(get_user_id())
# load bảng
@bp.route("/board", methods=["GET"])
def get_board():
    game = get_game()
    color = game.board.turn
    return jsonify({
        "board": game.get_board_state(),
        "turn": "white" if color == WHITE else "black"
    })
# nước đi hợp lệ legalmove
@bp.route("/legal-moves", methods=["GET"])
def legal_moves():
    game = get_game()
    try:
        row = int(request.args.get("row", -1))
        col = int(request.args.get("col", -1))
    except ValueError:
        return jsonify({"error": "row/col phải là số"}), 400
    if not (0 <= row < 8 and 0 <= col < 8):
        return jsonify({"error": "row/col ngoài phạm vi"}), 400
    moves = game.get_legal_moves_for(row, col)
    return jsonify({"moves": moves})
# người chơi đánh
@bp.route("/move", methods=["POST"])
def move():
    game = get_game()
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
    # người chơi đánh
    success = game.apply_player_move(move)
    if not success:
        return jsonify({
            "status": "invalid",
            "board": game.get_board_state()

        }),422
    ai_move = None
    # Ai move
    try:
        if game.board.turn == game.ai_color:
            ai_move = game.compute_ai_move()
    except Exception as e:
        return jsonify({"error": f"AI error: {str(e)}"}), 500
    color = game.board.turn
    return jsonify({
        "status": "ok",
        "board": game.get_board_state(),
        "turn": "white" if color == WHITE else "black",
        "ai_move": ai_move

    })
# reset game
@bp.route("/reset", methods=["POST"])
def reset():
    user_id = get_user_id()
    store.reset(user_id)
    game = store.get_or_create(user_id)
    return jsonify({
        "board": game.get_board_state(),
        "turn": "white"
    })
# debug
@bp.route("/debug", methods=["GET"])
def debug():
    return jsonify(store.stats())
