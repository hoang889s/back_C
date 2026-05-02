from flask_socketio import emit, join_room, leave_room
from flask import request, session

from extensions import socketio  

from persistence.database import SessionLocal
from persistence.models import User, Game, Move, Room, RoomPlayer, Turn, GameResult
from persistence.repository.roomrepository import RoomRepository
from persistence.repository.roomplayerrepository import RoomPlayerRepository

from services.game_manager import GameManager
from services.analyzer import Analyzer

from core.utils.fen import fen_to_board, board_to_fen
from api.auth import _jwt_service

# =============================
# Helper: Services factory
# =============================
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
# AUTH SOCKET
# =============================
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None

    db = get_db()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()

# =============================
# CONNECT
# =============================
@socketio.on("connect")
def handle_connect(auth):
    token = auth.get("token") if auth else None
    if not token:
        print("[SOCKET] No token provided")
        return False
    
    payload = _jwt_service.decode(token)
    if not payload:
        print("[SOCKET] Invalid token")
        return False
    
    session["user_id"] = int(payload["sub"])
    print(f"[SOCKET] Connected user: {payload['username']} (ID: {payload['sub']})")
    return True

# =============================
# CREATE ROOM
# =============================
@socketio.on("create_room")
def handle_create_room(data=None):
    data = data or {}
    user = get_current_user()
    
    if not user:
        emit("error", {"message": "Unauthorized"})
        return
    
    db, room_repo, rp_repo, _, _ = get_repos()
    try:
        room = room_repo.create_room(
            owner_id=user.id,
            name=data.get("name", "Chess Room"),
            mode=data.get("mode", "human"),
        )
        # Add creator to room
        rp_repo.add_player(room.id, user.id)
        db.commit()  # ✅ Commit ngay sau khi tạo room
        
        # Join socket room
        join_room(room.code)
        
        print(f"[SOCKET] Room created: {room.code} by {user.username}")
        emit("room_created", {
            "room_code": room.code,
            "user_id": user.id,
            "username": user.username
        })
    except Exception as e:
        print(f"[SOCKET ERROR] create_room: {str(e)}")
        emit("error", {"message": str(e)})
    finally:
        db.close()

# =============================
# JOIN ROOM - ✅ FIXED VERSION
# =============================
@socketio.on("join_room")
def handle_join_room(data):
    user = get_current_user()
    if not user:
        emit("error", {"message": "Unauthorized"})
        return

    room_code = data.get("room_code")
    if not room_code:
        emit("error", {"message": "Room code required"})
        return

    db, room_repo, rp_repo, gm, _ = get_repos()
    try:
        # ✅ FIX 1: Lock the room row with FOR UPDATE to prevent race condition
        room = db.query(Room).filter(
            Room.code == room_code
        ).with_for_update().first()  # 🔒 LOCK the row!
        
        if not room:
            emit("error", {"message": "Room not found"})
            return

        # Check current player count
        player_count = rp_repo.count_players(room.id)
        if player_count >= 2:
            emit("error", {"message": "Room is full"})
            return

        # Add player if not already in room
        if not rp_repo.is_in_room(room.id, user.id):
            rp_repo.add_player(room.id, user.id)
            print(f"[DEBUG] Added {user.username} to room {room_code}")
            db.commit()  # ✅ FIX 2: COMMIT immediately so other connections see the change
        
        # Join socket room
        join_room(room_code)
        print(f"[SOCKET] {user.username} joined room {room_code}")

        # ✅ FIX 3: Recount after commit to get accurate count
        updated_count = rp_repo.count_players(room.id)
        print(f"[DEBUG] Room {room_code} now has {updated_count} players")
        
        game_id = None
        
        if updated_count == 2:
            print(f"[SOCKET] Room {room_code} now has 2 players, creating game...")
            
            existing_game = gm.game_repo.get_by_room_id(room.id)
            if not existing_game:
                # Get players in order
                players = db.query(RoomPlayer).filter(
                    RoomPlayer.room_id == room.id
                ).order_by(RoomPlayer.created_at).all()
                
                print(f"[DEBUG] Players in DB: {[(p.user_id, p.created_at) for p in players]}")
                
                if len(players) != 2:
                    print(f"[ERROR] Expected 2 players, got {len(players)}")
                    emit("error", {"message": "Player count mismatch"})
                    return
                
                white_id = players[0].user_id
                black_id = players[1].user_id
                
                print(f"[SOCKET] Creating game: white={white_id}, black={black_id}")
                
                game = gm.game_repo.create_game(
                    room_id=room.id,
                    white_id=white_id,
                    black_id=black_id,
                )
                
                print(f"[DEBUG] Game created: {game.id}, white={game.white_player_id}, black={game.black_player_id}")
                
                # Update room with game_id
                room.game_id = game.id
                room.player_count = 2
                db.commit()
                print(f"[DEBUG] Updated Room: game_id={game.id}, player_count=2")
                
                game_id = game.id
                
            else:
                game = existing_game
                game_id = game.id
                print(f"[DEBUG] Using existing game: {game.id}")

            board = fen_to_board(game.fen)
            game_room = f"game_{game.id}"
            
            join_room(game_room)
            
            # Broadcast game_created to all in room
            socketio.emit("game_created", {
                "game_id": game.id,
                "room_code": room_code
            }, room=room_code)

            # Broadcast game_state to all in game room
            print(f"[SOCKET] Broadcasting game_state: white={game.white_player_id}, black={game.black_player_id}")
            socketio.emit("game_state", {
                "gameId": game.id,
                "game_id": game.id,
                "room_code": room.code,
                "white": game.white_player_id,
                "black": game.black_player_id,
                "turn": game.turn.value,
                "status": game.status.value,
                "fen": game.fen,
                "board": serialize_board(board)
            }, room=game_room)
        else:
            print(f"[DEBUG] Only {updated_count} player(s), waiting for second player...")

        # Send room_joined with game_id
        emit("room_joined", {
            "user": user.username,
            "room_code": room_code,
            "user_id": user.id,
            "game_id": game_id
        })
        
        # Notify others
        socketio.emit("user_joined", {
            "user": user.username,
            "user_id": user.id
        }, room=room_code, include_self=False)

    except Exception as e:
        print(f"[SOCKET ERROR] join_room: {str(e)}")
        import traceback
        traceback.print_exc()
        emit("error", {"message": str(e)})
    finally:
        db.close()

# =============================
# JOIN GAME (direct join via game ID)
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
        if not game_id:
            emit("game_error", {"message": "Game ID required"})
            return

        game = gm.game_repo.get_game(game_id)
        if not game:
            emit("game_error", {"message": "Game not found"})
            return

        print(f"[SOCKET] {user.username} joining game {game_id}")
        print(f"[SOCKET] Game state before: white={game.white_player_id}, black={game.black_player_id}")

        # Assign black player if not already assigned and user is not white
        if not game.black_player_id and user.id != game.white_player_id:
            print(f"[SOCKET] Assigning {user.username} as black player")
            gm.game_repo.assign_black_player(game_id, user.id)
            game = gm.game_repo.get_game(game_id)

        print(f"[SOCKET] Game state after: white={game.white_player_id}, black={game.black_player_id}")

        board = fen_to_board(game.fen)
        game_room = f"game_{game_id}"
        
        join_room(game_room)

        print(f"[SOCKET] Broadcasting game_state to room {game_room}")
        socketio.emit("game_state", {
            "gameId": game.id,
            "game_id": game.id,
            "room_code": game.room.code if game.room else None,
            "white": game.white_player_id,
            "black": game.black_player_id,
            "turn": game.turn.value,
            "status": game.status.value,
            "fen": game.fen,
            "board": serialize_board(board)
        }, room=game_room)

        print(f"[SOCKET] Emitted game_state with white={game.white_player_id}, black={game.black_player_id}")

    except Exception as e:
        print(f"[SOCKET ERROR] join_game: {str(e)}")
        emit("game_error", {"message": str(e)})
    finally:
        db.close()

# =============================
# LEAVE ROOM
# =============================
@socketio.on("leave_room")
def handle_leave_room(data):
    user = get_current_user()
    if not user:
        return

    room_code = data.get("room_code")
    if not room_code:
        return

    db, room_repo, rp_repo, _, _ = get_repos()
    try:
        room = room_repo.get_by_code(room_code)
        if room:
            rp_repo.remove_player(room.id, user.id)
            db.commit()  # ✅ Commit để chắc
            print(f"[SOCKET] {user.username} left room {room_code}")

        leave_room(room_code)
        
        socketio.emit("user_left", {
            "user": user.username,
            "user_id": user.id
        }, room=room_code)
    finally:
        db.close()

# =============================
# LEAVE GAME
# =============================
@socketio.on("leave_game")
def handle_leave_game(data):
    user = get_current_user()
    game_id = data.get("game_id")
    
    if game_id:
        print(f"[SOCKET] {user.username if user else 'Unknown'} left game {game_id}")
        leave_room(f"game_{game_id}")

# =============================
# MOVE
# =============================
@socketio.on("move")
def handle_move(data):
    user = get_current_user()
    if not user:
        emit("error", {"message": "Unauthorized"})
        return

    print(f"[SOCKET] Move data: {data}")

    db, _, _, gm, _ = get_repos()
    try:
        game_id = data.get("game_id")
        
        # Parse move format
        if isinstance(data.get("move"), dict):
            fr = data["move"]["from"]
            to = data["move"]["to"]
            move_str = to_chess_notation(fr["row"], fr["col"]) + \
                to_chess_notation(to["row"], to["col"])
        else:
            move_str = data.get("move")

        print(f"[SOCKET] Processing move {move_str} for game {game_id}")

        # Make the move
        result = gm.make_move(
            game_id=game_id,
            move_str=move_str,
            player_id=user.id
        )
        
        # Record move in database
        gm.game_repo.add_move(game_id, move_str, user.id)
        db.commit()  # ✅ Commit ngay
        
        # Get updated game state
        game = gm.game_repo.get_game(game_id)
        board = fen_to_board(game.fen)

        # Broadcast move to all players in game
        socketio.emit("move", {
            "move": move_str,
            "turn": game.turn.value,
            "check": result.get("is_check", False),
            "checkmate": result.get("is_checkmate", False),
            "fen": game.fen,
            "board": serialize_board(board),
            "status": game.status.value
        }, room=f"game_{game_id}")

        print(f"[SOCKET] Move broadcasted: {move_str}")

    except Exception as e:
        print(f"[SOCKET ERROR] move: {str(e)}")
        emit("error", {"message": str(e)})
    finally:
        db.close()

# =============================
# AI MOVE
# =============================
@socketio.on("ai_move")
def handle_ai_move(data):
    db, _, _, gm, analyzer = get_repos()
    
    try:
        game_id = data.get("game_id")
        print(f"[SOCKET] AI move requested for game {game_id}")

        # Generate AI move
        result = gm.ai_move(game_id, analyzer)
        db.commit()  # ✅ Commit ngay
        
        # Get updated game state
        game = gm.game_repo.get_game(game_id)
        board = fen_to_board(game.fen)

        # Broadcast AI move to all players
        socketio.emit("ai_move", {
            **result,
            "fen": game.fen,
            "board": serialize_board(board),
            "turn": game.turn.value,
            "status": game.status.value
        }, room=f"game_{game_id}")

        print(f"[SOCKET] AI move broadcasted")

    except Exception as e:
        print(f"[SOCKET ERROR] ai_move: {str(e)}")
        emit("error", {"message": str(e)})
    finally:
        db.close()

# =============================
# CREATE GAME (legacy - use join_room instead)
# =============================
@socketio.on("create_game")
def handle_create_game(data=None):
    data = data or {}
    user = get_current_user()
    if not user:
        emit("error", {"message": "Unauthorized"})
        return

    db, room_repo, _, gm, _ = get_repos()
    try:
        room_code = data.get("room_code")
        room = room_repo.get_by_code(room_code)
        if not room:
            emit("error", {"message": "Room not found"})
            return

        game = gm.game_repo.create_game(
            room_id=room.id,
            white_id=user.id,
        )
        db.commit()  # ✅ Commit
        emit("game_created", {
            "game_id": game.id
        })
    finally:
        db.close()