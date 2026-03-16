from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime
import os
from database import SessionLocal
from models import User
auth_bp = Blueprint("auth",__name__,url_prefix="/auth")
# cau hinh jwt
JWT_SECRET = os.getenv("JWT_SECRET","change-me-in-production-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN",60 * 24)) # 24 giờ
# helpers
def generate_token(user_id:int,username:str)->str:
    payload ={
        "sub":user_id,
        "username":username,
        "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRES_MIN),
        "iat":datetime.datetime.utcnow(),
    }
    return jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGORITHM)
def decode_token(token:str)->dict|None:
    try:
        return jwt.decode(token,JWT_SECRET,algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
# Decorator bảo vệ route – dùng @login_required
def login_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        auth_header = request.headers.get("Authorization","")
        if not auth_header.startswith("Bearer "):
            # lỗi 401 là chưa đăng nhập được
            return jsonify({"status":"error","message":"thiếu token xác thực"}),401
        token = auth_header[7:]
        payload = decode_token(token)
        if not payload:
            return jsonify({"status":"error","message":"Token không hợp lệ hoặc hết hạn"}),401
        # gắn thông tin user vào request
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated
#  POST /auth/register   
@auth_bp.route("/register", methods = ["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    # validates
    if not username or not email or not password:
        # lỗi 400 request sai
        return jsonify({"status": "error", "message": "Vui lòng điền đầy đủ username, email và password"}), 400
    if len(username)<3:
        return jsonify({"status": "error", "message": "Username phải có ít nhất 3 ký tự"}), 400
    if len(password)<6:
        return jsonify({"status": "error", "message": "Password phải có ít nhất 6 ký tự"}), 400
    if "@" not in email:
        return jsonify({"status": "error", "message": "Email không hợp lệ"}), 400
    db:Session = SessionLocal()
    try:
        # kiểm tra trùng username /email
        if db.query(User).filter(User.username == username).first():
            # 409 Conflict = Request hợp lệ nhưng bị xung đột với trạng thái hiện tại của dữ liệu trên server.
            return jsonify({"status":"error","message":"Username đã tồn tại"}),409
        if db.query(User).filter(User.email == email).first():
            return jsonify({"status": "error", "message": "Email đã được đăng ký"}), 409
        user = User(
            username = username,
            email = email,
            password_hash = generate_password_hash(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        token = generate_token(user.id,user.username)
        return jsonify({
            "status":"ok",
            "message":"Đăng ký thành công",
            "token":token,
            "user":{
                "id":user.id,
                "username":user.username,
                "email":user.email,
            }
        }),201
    except Exception as e:
        db.rollback()
        return jsonify({"status":"error","message":f"Lỗi server: {str(e)}"}),500
    finally:
        db.close()
#  POST /auth/login
@auth_bp.route("/login", methods=["POST"])   
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"status": "error", "message": "Vui lòng nhập username và password"}), 400
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or not check_password_hash(user.password_hash,password):
            return jsonify({"status": "error", "message": "Username hoặc password không đúng"}), 401
        token = generate_token(user.id, user.username)
        return jsonify({
            "status":"ok",
            "message":"Đăng nhập thành công",
            "token":token,
            "user":{
                "id":user.id,
                "username":user.username,
                "email":user.email,
            }
        }),200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi server: {str(e)}"}), 500
    finally:
        db.close()
# GET /auth/me  – lấy thông tin user hiện tại (cần token)
@auth_bp.route("/me",methods=["GET"])
@login_required
def me():
    db:Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == request.current_user["sub"]).first()
        if not user:
            # không tìm thấy resource 404
            return jsonify({"status": "error", "message": "Không tìm thấy user"}), 404
        return jsonify({
            "status":"ok",
            "user":{
                "id": user.id,
                "username":user.username,
                "email":user.email,
                "created_at":user.created_at.isoformat() if user.created_at else None,
            }
        }),200
    finally:
        db.close()
#  POST /auth/logout  – client xóa token phía local, server stateless
@auth_bp.route("/logout",methods=["POST"])
@login_required
def logout():
    # JWT là stateless – logout thực sự là xóa token ở client
    return jsonify({"status": "ok", "message": "Đăng xuất thành công"}), 200
