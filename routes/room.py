from flask import Blueprint, request, jsonify, g
from database import SessionLocal
from auth import login_required
from services.room_service import RoomService

bp = Blueprint("rooms", __name__)

# =========================
# TẠO PHÒNG
# =========================
@bp.route("/rooms", methods=["POST"])
@login_required
def create_room():
    db = SessionLocal()
    service = RoomService(db)

    try:
        data = request.get_json()

        if not data or "name" not in data:
            return jsonify({
                "success": False,
                "message": "Thiếu tên phòng"
            }), 400

        room = service.create_room(g.user, data)

        return jsonify({
            "success": True,
            "room_code": room.code
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    finally:
        db.close()


# =========================
# VÀO PHÒNG
# =========================
@bp.route("/rooms/join", methods=["POST"])
@login_required
def join_room():
    db = SessionLocal()
    service = RoomService(db)

    try:
        data = request.get_json()

        print("JOIN DATA:", data)

        if not data or "code" not in data:
            return jsonify({
                "success": False,
                "message": "Thiếu mã phòng"
            }), 400

        code = data.get("code")

        if isinstance(code, dict):
            code = code.get("code")

        if not code or not isinstance(code, str):
            return jsonify({
                "success": False,
                "message": "Code không hợp lệ"
            }), 400

        password = data.get("password")

        room = service.join_room(g.user, code, password)

        return jsonify({
            "success": True,
            "message": "Joined",
            "room_id": room.id
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    finally:
        db.close()


# RỜI PHÒNG

@bp.route("/rooms/leave", methods=["POST"])
@login_required
def leave_room():
    db = SessionLocal()
    service = RoomService(db)

    try:
        data = request.get_json()

        if not data or "room_id" not in data:
            return jsonify({
                "success": False,
                "message": "Thiếu room_id"
            }), 400

        room_id = data.get("room_id")

        if not isinstance(room_id, int):
            return jsonify({
                "success": False,
                "message": "room_id không hợp lệ"
            }), 400

        service.leave_room(g.user, room_id)

        return jsonify({
            "success": True,
            "message": "Left room"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    finally:
        db.close()