from flask_socketio import emit, join_room, leave_room
from flask import request,session

from extensions import socketio  

from persistence.database import SessionLocal
from persistence.models import User,Game,Move,Room,RoomPlayer,Turn,GameResult
from persistence.repository.roomrepository import RoomRepository
from persistence.repository.roomplayerrepository import RoomPlayerRepository


from services.game_manager import GameManager
from services.analyzer import Analyzer

from core.utils.fen import fen_to_board, board_to_fen
from api.auth import _jwt_service

# =============================
# Helper: tạo service per-event 
# =============================
#def get_services():
#    db = SessionLocal()
#    gm = GameManager(db)
#    analyzer = Analyzer(depth=4)
#    return db, gm, analyzer
def get_db():
    return SessionLocal()
def get_repos():
    db = get_db()
    return (
        db,
        RoomRepository(db),
        RoomPlayerRepository(db),
        GameManager(db),
        Analyzer(depth=4)
)
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
# AUTH SOCKET  ok
# =============================
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None

    db =get_db()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


# =============================
# CONNECT ok
# =============================
@socketio.on("connect")
def handle_connect(auth):
    token = auth.get("token") if auth else None
    if not token:
        print("No token")
        return False
    payload = _jwt_service.decode(token)
    if not payload:
        print(" Invalid token")
        return False
    session["user_id"] = int(payload["sub"])
    print(" Socket connected:", payload["username"])


# =============================
# JOIN GAME ok f
# =============================
@socketio.on("join_game")
def handle_join_game(data):
    user = get_current_user()
    
    if not user:
        emit("game_error", {"message": "Unauthorized"})
        return
    db, _, _, gm, _ = get_repos()

    try:
        game_id = data.get("gameId")
        game = gm.game_repo.get_game(game_id)
        
        if not game:
            emit("game_error", {"message": "Game not found"})
            return
        # gán players
        if not game.black_player_id and user.id != game.white_player_id:
            gm.game_repo.assign_black_player(game_id, user.id)
        board = fen_to_board(game.fen)
        room = f"game_{game_id}"
        join_room(room)
        socketio.emit("game_state", {
            "gameId": game.id,
            "white": game.white_player_id,
            "black": game.black_player_id,
            "turn": game.turn.value,
            "status": game.status.value,
            "fen":game.fen,
            "board": serialize_board(board)
        },
        room=room)

    finally:
        db.close()

# =============================
# JOIN ROOM ok f
# =============================
@socketio.on("join_room")
def handle_join(data):
    user = get_current_user()
    if not user:
        emit("error", {"message": "Unauthorized"})
        return

    room_code = data.get("room_code")
    if not room_code:
        emit("error", {"message": "Unauthorized"})
        return
    #join_room(room_code)
    #db = SessionLocal()
    db, room_repo, rp_repo, _, _ = get_repos()
    try:
        #room_repo = RoomRepository(db)
        #rp_repo = RoomPlayerRepository(db)
        room = room_repo.get_by_code(room_code)
        if not room:
            emit("error", {"message": "Room not found"})
            return
        #  check full (chess = 2 player)
        if rp_repo.count_players(room.id) >= 2:
            emit("error", {"message": "Room is full"})
            return
        #  tránh duplicate
        if not rp_repo.is_in_room(room.id, user.id):
            rp_repo.add_player(room.id, user.id)

        join_room(room_code)
        emit("joined", {
            "user": user.username,
            "room": room_code

        })
        socketio.emit("user_joined", {
            "user": user.username
        },room=room_code, include_self=False)
        print(f"[SOCKET] {user.username} joined room {room_code}")
    finally:
        db.close()



# =============================
# LEAVE ROOM ok f
# =============================
@socketio.on("leave_room")
def handle_leave(data):
    user = get_current_user()
    room_code = data.get("room_code")
    if not user or not room_code:
        return
    db, room_repo, rp_repo, _, _ = get_repos()
    # db = SessionLocal()
    #db, room_repo, rp_repo, _, _ = get_repos()
    try:
        #room = db.query(Room).filter(Room.code == room_code).first()
        room = room_repo.get_by_code(room_code)
        if room:
            #rp_repo = RoomPlayerRepository(db)
            rp_repo.remove_player(room.id, user.id)
        leave_room(room_code)
        socketio.emit("user_left", {
            "user": user.username
        },room=room_code)
    finally:
        db.close()
# =============================
# LEAVE GAME ok
# =============================
@socketio.on("leave_game")
def handle_leave_game(data ):
    game_id = data.get("game_id")
    if game_id:
        leave_room(f"game_{game_id}")
    

# =============================
# CREATE GAME ok f
# =============================
@socketio.on("create_game")
def handle_create_game(data = None):
    data = data or {}
    user = get_current_user()
    if not user:
        emit("error", {"message": "Unauthorized"})
        return
    #db, gm, _ = get_services()
    #db = SessionLocal()
    db, room_repo, _, gm, _ = get_repos()

    try:
        room_code = data.get("room_code")
        #room = db.query(Room).filter(Room.code == room_code).first()
        room = room_repo.get_by_code(room_code)
        if not room:
            emit("error", {"message": "Room not found"})
            return
        game = gm.game_repo.create_game(
            room_id=room.id,
            white_id=user.id,
        )
        emit("game_created", {
            "game_id": game.id
        })

    finally:
        db.close()


# =============================
# MOVE ok
# =============================
@socketio.on("move")
def handle_move(data):
    user = get_current_user()
    if not user:
        emit("error", {"message": "Unauthorized"})
        return

    print("[DEBUG DATA]:", data)


    #db, gm, _ = get_services()
    db, _, _, gm, _ = get_repos()

    try:
        game_id = data.get("game_id")
        # parse move
        if isinstance(data.get("move"), dict):
            fr = data["move"]["from"]
            to = data["move"]["to"]
            move_str = to_chess_notation(fr["row"], fr["col"]) + \
                to_chess_notation(to["row"], to["col"])
        else:
            move_str = data.get("move")
        result = gm.make_move(
            game_id=game_id,
            move_str=move_str,
            player_id=user.id
        )
        gm.game_repo.add_move(game_id, move_str, user.id)
        game = gm.game_repo.get_game(game_id)
        board = fen_to_board(game.fen)
        socketio.emit("move", {
            "move": move_str,
            "turn": game.turn.value,
            "check": result.get("is_check"),
            "checkmate": result.get("is_checkmate"),
            "fen":game.fen,
            "board": serialize_board(board),

        },room=f"game_{game_id}")

    finally:
        db.close()

# =============================
# CREATE ROOM  ok f
# =============================
@socketio.on("create_room")
def handle_create_room(data=None):
    data = data or {}
    user = get_current_user()
    #print("[DEBUG DATA]:", data)
    if not user:
        emit("error", {"message": "Unauthorized"})
        return
    #db = SessionLocal()
    #db, gm, _ = get_services()
    db, room_repo, rp_repo, _, _ = get_repos()
    try:
        #room_repo = RoomRepository(db)
        #rp_repo = RoomPlayerRepository(db)
        room = room_repo.create_room(
            owner_id=user.id,
            name=data.get("name", "Chess Room"),
            mode=data.get("mode", "human"),

            )
        # add user vào room DB
        rp_repo.add_player(room.id, user.id)
        # join socket room luôn
        join_room(room.code)
        emit("room_created",{
            "room_code": room.code
        })
        print(f"[SOCKET] Room created: {room.code}")
    finally:
        db.close()
        

# =============================
# AI MOVE f
# =============================
@socketio.on("ai_move")
def handle_ai(data):
    #db = SessionLocal()
    #gm = GameManager(db)
    #analyzer = Analyzer(depth=4)
    db, _, _, gm, analyzer = get_repos()

    try:
        game_id = data.get("game_id")

        result = gm.ai_move(game_id, analyzer)
        game = gm.game_repo.get_game(game_id)
        board = fen_to_board(game.fen)


       

        socketio.emit("ai_move", {
            **result,
            "fen": game.fen,
            "board": serialize_board(board),
            "turn": game.turn.value,
        },room=f"game_{game_id}")

    except Exception as e:
        emit("error", {"message": str(e)})

    finally:
        db.close()