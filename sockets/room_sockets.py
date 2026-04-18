from flask_socketio import join_room, leave_room, emit,SocketIO
from flask import request
from storage.room_manager import Room,room_manager
from constants import WHITE, BLACK
#from app import socketio
from extensions import socketio
# join room
@socketio.on("join_room")
def handle_join(data):
    room_code = data["room_code"]
    user_id = data.get("user_id")
    room = room_manager.get_room(room_code)
    if not room:
        emit("error",{"message": "Room không tồn tại"}, room=request.sid)
        return
    result = room_manager.join_room(room_code, user_id)
    if "error" in result:
        emit("error", result, room=request.sid)
        return
    join_room(room_code)
    emit("user_joined", {
        "user_id": user_id,
        "players": room.players
    })
    emit("game_state", {
        "board": room.board.board,
        "turn": room.board.turn
    },room=request.sid)
# move
@socketio.on("move")
def handle_move(data):
    room_code = data["room_code"]
    move = tuple(data["move"])
    user_id = data.get("user_id")

    room = room_manager.get_room(room_code)
    if not room:
        emit("error", {"message": "Room không tồn tại"}, room=request.sid)
        return
    result = room.make_move(user_id, move)
    if "error" in result:
        emit("error", result, room=request.sid)
        return
    emit("move", {
        "move": move,
        "board": result["board"],
        "turn": result["turn"]
    },room=room_code)
    if room.board.is_checkmate(room.board.turn):
        emit("game_over", {
            "type": "checkmate",
        },room=room_code)
# leave 
@socketio.on("leave_room")
def handle_leave(data):
    room_code = data["room_code"]
    user_id = data.get("user_id")
    leave_room(room_code)
    room = room_manager.get_room(room_code)
    if not room:
        return
    room_manager.leave_room(room_code, user_id)
    emit("user_left", {
        "user_id":user_id,
    },room=room_code)