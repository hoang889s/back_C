from flask import Blueprint, request, jsonify, g
from database import SessionLocal
from auth import login_required
from services.room_service import RoomService
bp = Blueprint("rooms",__name__)
# tao phong
@bp.route("/rooms",methods=["POST"])
@login_required
def create_room():
    db = SessionLocal()
    service = RoomService(db)
    try:
        room = service.create_room(g.user,request.json)
        return jsonify({"room_code": room.code})
    except Exception as e:
        return {"error": str(e)}, 400
    finally:
        db.close()
# vao phong
@bp.route("/rooms/join", methods=["POST"])
@login_required
def join_room():
    db = SessionLocal()
    service = RoomService(db)
    try:
        data = request.json
        room = service.join_room(g.user,data["code"],data.get("password"))
        return {"message": "Joined", "room_id": room.id}
    except Exception as e:
        return {"error": str(e)}, 400
    finally:
        db.close()
# roi phong
@bp.route("/rooms/leave", methods=["POST"])
@login_required
def leave_room():
    db = SessionLocal()
    service = RoomService(db)
    try:
        service.leave_room(g.user, request.json["room_id"])
        return {"message": "Left room"}
    except Exception as e:
        return {"error": str(e)}, 400
    finally:
        db.close()

    