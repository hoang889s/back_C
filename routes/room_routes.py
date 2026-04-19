from flask import Blueprint, request, jsonify
from store.room_store import RoomStore
bp = Blueprint("room", __name__)
store = RoomStore()
def get_user_id():
    uid = request.headers.get("X-User-Id")
    if not uid:
        uid = f"guest-{request.remote_addr}"
    return uid
# routes
# join room
@bp.route("/room/<room_id>/join", methods=["POST"])
def join(room_id):
    user_id = get_user_id()
    try:
        room = store.join_room(room_id, user_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({
        "room_id": room_id,
        "players": room["players"]
    })
# leave room
@bp.route("/room/<room_id>/leave", methods=["POST"])
def leave(room_id):
    user_id = get_user_id()
    store.remove_player(room_id, user_id)
    return jsonify({
        "status": "left",
        "room_id": room_id
    })
# trạng thái state
@bp.route("/room/<room_id>/state", methods=["GET"])
def state(room_id):
    state = store.get_state(room_id)
    if not state:
        return jsonify({"error": "Phòng không tồn tại"}), 404
    return jsonify(state)
# lấy bàn cờ
@bp.route("/room/<room_id>/board", methods=["GET"])
def board(room_id):
    state = store.get_state(room_id)
    if not state:
         return jsonify({"error": "Phòng không tồn tại"}), 404
    return jsonify({
        "board": state["board"],
        "turn": state["turn"],
        "players": state["players"]
    })
# người chơi đánh
@bp.route("/room/<room_id>/move", methods=["POST"])
def move(room_id):
    user_id = get_user_id()
    room = store.get_room(room_id)
    if not room:
        return jsonify({"error": "phòng không tồn tại"}), 404
    # check người chơi trong phòng
    player = next((p for p in room["players"] if p["user_id"] == user_id), None)
    if not player:
        return jsonify({"error": "Bạn chưa vào room"}), 403
    game = room["game"]
    data = request.get_json(silent=True) or {}
    try:
        from_sq = data["from"]
        to_sq = data["to"]
        move = (
            from_sq["row"], from_sq["col"],
            to_sq["row"], to_sq["col"]
        )
    except Exception:
        return jsonify({"error": "Dữ liệu không hợp lệ"}), 400
    # check đúng lượt
    current_turn = "white" if game.board.turn == 1 else "black"
    if player["color"] != current_turn:
        return jsonify({"error": "Không phải lượt của bạn"}), 403
    # di chuyển
    try:
        game.make_move(move)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({
        "status": "ok",
        "board": game.get_board_state(),
        "turn": "white" if game.board.turn == 1 else "black",
        "players": room["players"]
    })
# reset
@bp.route("/room/<room_id>/reset", methods=["POST"])
def reset(room_id):
    room = store.get_room(room_id)
    if not room:
        return jsonify({"error": "Room not found"}), 404
    room["game"].reset()
    return jsonify({
        "status": "reset",
        "board": room["game"].get_board_state(),
        "turn": "white"
    })
# nếu nâng cấp hãy nghĩ đến socketsio ở đây