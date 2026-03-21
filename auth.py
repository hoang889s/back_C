from datetime import datetime,timedelta
import os 
#import datetime
from functools import wraps

import jwt
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

from database import SessionLocal, init_db   # SQLServerDatabase instance
from models import User

class JWTConfig:
    # đăng ký token
    SECRET    = os.getenv("JWT_SECRET", "change-me-in-production-secret-key")
    # kiểu mã hóa 
    ALGORITHM = "HS256"
    # thời gian tới hạn
    EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", 60 * 24*7))   
#  JWT Service – thuần logic, không phụ thuộc Flask
class JWTService:
    # hàm khởi tạo
    def __init__(self,config:JWTConfig|None=None):
        self.cfg = config or JWTConfig()
    # hàm sinh token truyền vào user_id và username
    def generate(self,user_id:int,username:str)->str:
        # lấy thời gian hiện tại
        now = datetime.utcnow()
        # payload nơi chứa dữ liệu của jwt token nó có dạng HEADER.PAYLOAD.SIGNATURE
        payload={
            "sub":str(user_id),
            "username":username,
            "iat":now,
            "exp":now + timedelta(minutes=self.cfg.EXPIRES_MIN), 

        }
        # trả về dạng jwt
        return jwt.encode(payload,self.cfg.SECRET,algorithm=self.cfg.ALGORITHM)
    # hàm giải mã jwt
    def decode(self,token:str)->dict | None:
        try:
            # xác thực và giải mã jwt
            print(f"[JWT DECODE] dùng SECRET = '{self.cfg.SECRET}'")
            return jwt.decode(token,self.cfg.SECRET,algorithms=[self.cfg.ALGORITHM])
        except jwt.ExpiredSignatureError:
            print("[JWT] hết hạn")
            return None
        except jwt.InvalidTokenError as e:
            print(f"[JWT] không hợp lệ: {e}")
            return None
# Auth Service – business logic (register/login)
class AuthService:
    # khởi tạo
    def __init__(self,database=None,jwt_service:JWTService|None=None):
        self._jwt = jwt_service or JWTService()
    def get_session(self)->Session:
        return SessionLocal()
    # hàm đăng ký POST
    def register(self,username:str,email:str,password:str)->dict:
        # kiểm tra email có hợp lệ hay không
        self._validate_register(username,email,password)
        session = self.get_session()
        try:
        # tự động mở session và rollback nếu có lỗi
        #with self._db.get_session() as session:
            # kiểm tra username và email có bị trùng không
            self._assert_unique(session,username,email)
            # tạo subject user mới
            user = User(
                username = username,
                email = email,
                password_hash = generate_password_hash(password),
            )
            # thêm vào database
            session.add(user)
            # thêm vào nhưng chưa commit
            session.flush()
            # tạo token
            token = self._jwt.generate(user.id,user.username)
            return{
                "token":token,
                "user":self._serialize(user),
            }
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    # hàm đăng nhập POST
    def login(self,username:str,password:str)->dict:
        # nếu không username hoặc password null nhả lỗi
        if not username or not password:
            raise ValueError("Vui lòng nhập username và password")
        session = self.get_session() 
        # tự động mở session và rollback nếu có lỗi
        # with self._db.get_session() as session:
        try:
            # tìm kiếm user trong db tương đương với select * from users where username = username
            user = session.query(User).filter(User.username==username).first()
            # kiểm tra có đúng là user không và kiểm tra password có đúng không
            if not user or not check_password_hash(user.password_hash,password):
                raise ValueError("Sai username hoặc password")
            # tạo token
            token = self._jwt.generate(user.id,user.username)
            return{
                "token":token,
                "user": self._serialize(user),
            }
        finally:
            session.close()
    # hàm lấy thông tin user GET
    def get_user(self,user_id:int)->dict:
            session = self.get_session()  
            # tìm kiếm user trong db tương đương với SELECT * FROM users WHERE id = ? LIMIT 1
            user = session.query(User).filter(User.id == int(user_id)).first()
            # nếu không tìm thấy user nhả lỗi
            if not user:
                raise LookupError("không tìm thấy user")
            # trả thông tin user
            return self._serialize(user,full = True)
    # decorator biến hàm thành phương thức tĩnh + không dùng self, thuần logic k, không thuộc tính object
    @staticmethod
    # kiểm tra thông tin đăng ký
    def _validate_register(username:str,email:str,password:str)->None:
        # nếu dư liệu rỗng thì nhả lỗi nhập đầy đủ
        if not username or not email or not password:
            raise ValueError("Vui lòng nhập đầy đủ thông tin username,email,password")
        # kiểm tra độ dài username 
        if len(username) < 3:
            raise ValueError("username phải có ít nhất 3 ký tự")
        # kiểm tra độ dài password
        if len(password) < 6:
            raise ValueError("password phải có ít nhất 6 ký tự")
        # kiểm tra có @ hay không
        if "@" not in email:
            raise ValueError("email phải có @") 
    @staticmethod
    # kiểm tra có trùng username hay email không
    def _assert_unique(session:Session,username:str,email:str)->None:
        # nếu tìm thấy user thì nhả lỗi
        if session.query(User).filter(User.username == username).first():
            raise LookupError("__conflict__username__")
        # nếu tìm thấy email thì nhả lỗi
        if session.query(User).filter(User.email == email).first():
            raise LookupError("__conflict__email__")
    @staticmethod
    # hàm chuyển đổi object user thành dict
    def _serialize(user:User,full:bool=False)->dict:
        # tạo user cơ bản tránh attribute error
        base = {"id": user.id, "username": user.username, "email": user.email,"role": user.role.value,}
        # nếu full đúng thì trả thêm dữ liệu hasattr kiểm tra object có thuộc tính này không
        if full and hasattr(user,"created_at"):
            # thêm created_at vào base
            base["created_at"] = user.created_at.isoformat() if user.created_at else None
        return base
# Auth Blueprint – chỉ lo HTTP layer , tiến vào api
class AuthBlueprint:
    # khởi tạo
    def __init__(self,auth_service:AuthService|None=None,jwt_service:JWTService|None = None,url_prefix:str="/auth"):
        self._svc = auth_service or AuthService()
        self._jwt = jwt_service or JWTService()
        self.blueprint = Blueprint("auth",__name__,url_prefix=url_prefix)
        self._register_routes()
    # kiểm tra token trước khi chạy api
    def login_required(self,f):
        # bảo vệ giữ hàm gốc
        @wraps(f)
        # khi api được gọi vd profile nhưng lại goi decorated không chạy trực tiếp prfile
        # giúp backend biết người chơi đang làm gì
        def decorrated(*args,**kwargs):
            # lấy header token
            header = request.headers.get("Authorization","")
            # nếu header token không tồn tại
            if not header.startswith("Bearer "):
                # nhả lỗi 401 Unauthorized có thể là lỗi token sai 
                return jsonify({"status": "error", "message": "Thiếu token xác thực"}), 401
            # bỏ phần đâu lấy phần sau đó
            payload = self._jwt.decode(header[7:])
            if not payload:
                # lỗi 401 token không hợp lệ hoặc hết hạn
                return jsonify({"status": "error", "message": "Token không hợp lệ hoặc hết hạn"}),401
            # lưu user vào request
            request.current_user = payload
            # gọi api thật
            return f(*args, **kwargs)
        return decorrated
    # hàm routes đăng ký
    def _register_routes(self):
        # group các routes /api/register
        bp = self.blueprint
        # đăng ký route
        @bp.route("/register",methods=["POST"])
        def register():
            # lấy data từ request hoặc trả về rỗng
            data     = request.get_json(silent=True) or {}
            # lấy tên user bỏ khoảng trắng ở đầu và cuối
            username = (data.get("username") or "").strip()
            # lấy email bỏ khoảng trắng và bỏ chữ hoa
            email = (data.get("email") or "").strip().lower()
            # lấy mật khẩu
            password = (data.get("password") or "").strip()
            try:
                # kết quả
                result = self._svc.register(username, email, password)
                # thành công mã 200
                return jsonify({"status": "ok", "message": "Đăng nhập thành công", **result}), 200
            except ValueError as e:
                # lỗi 400 client gửi request sai nên server không nhận
                return jsonify({"status": "error", "message": str(e)}), 400
            except PermissionError as e:
                # sai token hoặc chưa đăng nhập 401
                return jsonify({"status": "error", "message": str(e)}), 401
            except Exception as e:
                # lỗi từ server có thể là lỗi chính hoặc logic
                return jsonify({"status": "error", "message": f"Lỗi server: {e}"}), 500
        # đăng nhập route
        @bp.route("/login", methods = ["POST"])
        def login():
            # lấy data
            data = request.get_json(silent=True) or {}
            # tên 
            username = (data.get("username") or "").strip()
            # mật khẩu
            password = (data.get("password") or "").strip()
            try:
                result = self._svc.login(username, password)
                # thành công mã 200
                return jsonify({"status": "ok", "message": "Đăng nhập thành công", **result}), 200
            except ValueError as e:
                # lỗi 400 server đã nhận nhưng token sai
                return jsonify({"status": "error", "message": str(e)}), 400
            except PermissionError as e:
                # lỗi 401 token sai
                return jsonify({"status": "error", "message": str(e)}), 401
            except Exception as e:
                # lỗi 500 server sai    
                return jsonify({"status": "error", "message": f"Lỗi server: {e}"}), 500
        @bp.route("/me" ,methods = ["GET"])
        @self.login_required
        # lấy thông tin người dùng
        def me():
            try:
                # lấy thông tin
                user = self._svc.get_user(request.current_user["sub"])
                # thành công
                return jsonify({"status": "ok", "user": user}), 200
            except LookupError as e:
                # not found server không tìm thấy tài nguyên
                return jsonify({"status": "error", "message": str(e)}), 404
        @bp.route("/logout", methods=["POST"])
        @self.login_required
        def logout():
            # 200 thành công
            return jsonify({"status": "ok", "message": "Đăng xuất thành công"}), 200
# Tạo các instance mặc định
_jwt_service  = JWTService()
_auth_service = AuthService(jwt_service=_jwt_service)
_auth_blueprint = AuthBlueprint(
    auth_service=_auth_service,
    jwt_service=_jwt_service,
)
# Export để app.py import
auth_bp       = _auth_blueprint.blueprint
login_required = _auth_blueprint.login_required






    










