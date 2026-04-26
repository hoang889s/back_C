from flask_socketio import emit, join_room, leave_room
from flask import request

from extensions import socketio  

from persistence.database import SessionLocal
from persistence.models import User
from api.auth import _jwt_service

from services.game_manager import GameManager
from services.analyzer import Analyzer


# =============================
# Helper: tạo service per-event
# =============================
def get_services():
    db = SessionLocal()
    gm = GameManager(db)
    analyzer = Analyzer(depth=4)
    return db, gm, analyzer
def serialize_board(board):
    return [
        ["" if cell == "." else cell for cell in row]
        for row in board.board
    ]
def to_chess_notation(row, col):
    col_char = chr(col + ord('a'))
    row_char = str(8 - row)
    return col_char + row_char


# =============================
# AUTH SOCKET
# =============================
def get_current_user():
    token = request.args.get("token")
    if not token:
        return None

    payload = _jwt_service.decode(token)
    if not payload:
        return None

    session = SessionLocal()
    try:
        return session.query(User).filter(
            User.id == int(payload["sub"])
        ).first()
    finally:
        session.close()


# =============================
# CONNECT
# =============================
@socketio.on("connect")
def handle_connect():
    user = get_current_user()
    if not user:
        return False

    print(f"[SOCKET] {user.username} connected")
# =============================
# JOIN GAME
# =============================
@socketio.on("join_game")
def handle_join_game(data):
    user = get_current_user()
    if not user:
        emit("game_error", {"message": "Unauthorized"})
        return
    db, gm, _ = get_services()
    try:
        game_id = data.get("gameId")
        if not game_id:
            emit("game_error", {"message": "gameId is required"})
            return
        print(f"[SOCKET] User {user.username} joining game {game_id}")
        game = gm.load_game(game_id)
        if not game:
            emit("game_error", {"message": f"Game {game_id} not found"})
            return
        room_id = f"game_{game_id}"
        join_room(room_id)


        players = game.get("players", [])
        if len(players) >=2:
            game["status"] = "playing"
            print("[SOCKET] Game started!")
            emit("game_start", {
                "status": "playing"
            },room = room_id)




        print(f"[SOCKET] {user.username} joined room {room_id}")
        board_data = serialize_board(game["board"])
        print("BOARD DATA:", board_data)
        socketio.emit("game_state", {
            "gameId": game_id,
            "board": board_data,
            "currentTurn": game.get("current_turn", "white"),
            "status": game.get("status", "waiting"),
            "players": players,
            "winner": game.get("winner", None),
            "moves": game.get("moves", []),
        },room=room_id)
        print(f"[SOCKET] Sent game_state for game {room_id}")
    except Exception as e:
        print(f"[SOCKET ERROR] {str(e)}")
        emit("game_error", {"message": str(e)})
    finally:
        db.close()

# =============================
# JOIN ROOM
# =============================
@socketio.on("join_room")
def handle_join(data):
    user = get_current_user()
    if not user:
        emit("error", {"message": "Unauthorized"})
        return

    room_code = data.get("room_code")
    join_room(room_code)

    emit("joined", {
        "user": user.username,
        "room": room_code
    }, room=room_code)


# =============================
# LEAVE ROOM
# =============================
@socketio.on("leave_room")
def handle_leave(data):
    room_code = data.get("room_code")
    leave_room(room_code)
# =============================
# LEAVE GAME
# =============================
@socketio.on("leave_game")
def handle_leave_game(data =None):

    user = get_current_user()
    if not user:
        return
 
    print(f"[SOCKET] User {user.username} left game")
    # Leave all rooms
    leave_room(None)

# =============================
# CREATE GAME
# =============================
@socketio.on("create_game")
def handle_create(data):
    db, gm, _ = get_services()
    try:
        room_code = data.get("room_code")

        game = gm.create_game(room_code)

        socketio.emit("game_created", {
            "game_id": game.id
        }, room=room_code)

    except Exception as e:
        emit("error", {"message": str(e)})

    finally:
        db.close()


# =============================
# MOVE
# =============================
@socketio.on("move")
def handle_move(data):
    user = get_current_user()
    if not user:
        emit("error", {"message": "Unauthorized"})
        return

    print("[DEBUG DATA]:", data)

    db, gm, _ = get_services()

    try:
        game_id = data.get("game_id")
        if not game_id:
            emit("error", {"message": "Missing game_id"})
            return
        if "move" in data and isinstance(data["move"], dict):
            fr = data["move"]["from"]
            to = data["move"]["to"]
            move_str = to_chess_notation(fr["row"], fr["col"]) + \
                            to_chess_notation(to["row"], to["col"])
        elif "move" in data and isinstance(data["move"], str):
            move_str = data["move"]
        else:
            emit("error", {"message": "Invalid move format"})
            return
        print("FINAL MOVE STR:", move_str, type(move_str))



        result = gm.make_move(
            game_id=game_id,
            move_str=move_str,
            player_id=user.id
        )

        game = gm.load_game(game_id)
        room_id = f"game_{game_id}"
        board_data = serialize_board(game["board"])

        socketio.emit("move", {
            "move": move_str,
            "board": board_data,
            "currentTurn": result["turn"],
            "check": result["is_check"],
            "checkmate": result["is_checkmate"]
        }, room=room_id)

    except Exception as e:
        print(f"[SOCKET ERROR] {str(e)}")
        emit("error", {"message": str(e)})

    finally:
        db.close()


# =============================
# AI MOVE
# =============================
@socketio.on("ai_move")
def handle_ai(data):
    db, gm, analyzer = get_services()
    try:
        game_id = data.get("game_id")

        result = gm.ai_move(game_id, analyzer)

        game = gm.load_game(game_id)
        #room_id = game.get("room_id")
        room_id= f"game_{game_id}"
        board_data = serialize_board(game["board"])

        socketio.emit("ai_move", {
            **result,
            "board": board_data,

        },room=room_id)

    except Exception as e:
        emit("error", {"message": str(e)})

    finally:
        db.close()