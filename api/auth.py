from datetime import datetime, timedelta
import os
from functools import wraps

from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

from persistence.database import SessionLocal
from persistence.models import User
# =====================================================
# CONFIG
# =====================================================
class JWTConfig:
    SECRET = os.getenv("JWT_SECRET", "change-me-in-production-secret-key")
    ALGORITHM = "HS256"
    EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", 60 * 24 * 7))
# =====================================================
# JWT SERVICE (SOURCE OF TRUTH)
# =====================================================
class JWTService:
    def __init__(self, config: JWTConfig | None = None):
        self.cfg = config or JWTConfig()
    def generate(self, user_id: int, username: str) -> str:
        import jwt
        now  = datetime.utcnow()
        payload = {
            "sub": str(user_id),
            "username": username,
            "iat": now,
            "exp": now + timedelta(minutes=self.cfg.EXPIRES_MIN),
        }
        return jwt.encode(payload, self.cfg.SECRET, algorithm=self.cfg.ALGORITHM)
    def decode(self, token: str) -> dict | None:
        import jwt
        try:
            return jwt.decode(
                token,
                self.cfg.SECRET,
                algorithms=[self.cfg.ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
# GLOBAL JWT SERVICE (DUY NHẤT)
_jwt_service = JWTService()
# =====================================================
# AUTH SERVICE (BUSINESS LOGIC)
# =====================================================
class AuthService:
    def __init__(self, jwt_service: JWTService = None):
        self._jwt = jwt_service or _jwt_service
    def get_session(self):
        return SessionLocal()
    # -------------------------
    # REGISTER
    # -------------------------
    def register(self, username: str, email: str, password: str) -> dict:
        self._validate(username, email, password)
        db = self.get_session()
        try:
            self._assert_unique(db, username, email)
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role="user"
            )
            db.add(user)
            db.flush()
            token = self._jwt.generate(user.id, user.username)
            db.commit()
            return {
                "token": token,
                "user": self._serialize(user),
            }
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    # -------------------------
    # LOGIN
    # -------------------------
    def login(self, username: str, password: str) -> dict:
        if not username or not password:
            raise ValueError("Thiếu username/password")
        db = self.get_session()
        try:
            user = db.query(User).filter(User.username == username).first()

            if not user or not check_password_hash(user.password_hash, password):
                raise ValueError("Sai tài khoản hoặc mật khẩu")
            token = self._jwt.generate(user.id, user.username)
            return {
                "token": token,
                "user": self._serialize(user),
            }
        finally:
            db.close()
    # -------------------------
    # GET USER
    # -------------------------
    def get_user(self, user_id: int):
        db = self.get_session()
        try:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                raise LookupError("User không tồn tại")
            return self._serialize(user, full=True)
        finally:
            db.close()
    # =====================================================
    # VALIDATION
    # =====================================================
    @staticmethod
    def _validate(username, email, password):
        if not username or not email or not password:
            raise ValueError("Thiếu dữ liệu")
        if len(username) < 3:
            raise ValueError("Username >= 3 ký tự")
        if len(password) < 6:
            raise ValueError("Password >= 6 ký tự")
        if "@" not in email:
            raise ValueError("Email không hợp lệ")
    @staticmethod
    def _assert_unique(db: Session, username: str, email: str):
        if db.query(User).filter(User.username == username).first():
            raise ValueError("USERNAME_EXISTS")
        if db.query(User).filter(User.email == email).first():
            raise ValueError("EMAIL_EXISTS")
    @staticmethod
    def _serialize(user: User, full: bool = False):
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
        if full and hasattr(user, "created_at"):
            data["created_at"] = user.created_at.isoformat()
        return data
# =====================================================
# HTTP AUTH MIDDLEWARE
# =====================================================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "missing token"}), 401
        token = auth[7:]
        payload = _jwt_service.decode(token)
        if not payload:
            return jsonify({"error": "invalid token"}), 401
        db = SessionLocal()
        try:
            user = db.query(User).filter(
                User.id == int(payload["sub"])

            ).first()
            if not user:
                return jsonify({"error": "user not found"}), 401
            g.user = user
            return f(*args, **kwargs)
        finally:
            db.close()
    return wrapper
# =====================================================
# BLUEPRINT
# =====================================================
class AuthBlueprint:
    def __init__(self, service: AuthService = None, url_prefix="/api/auth"):
        self._svc = service or AuthService()
        self.blueprint = Blueprint("auth", __name__, url_prefix=url_prefix)
        self._routes()
    def _routes(self):
        bp = self.blueprint
        @bp.route("/register", methods=["POST"])
        def register():
            data = request.get_json() or {}
            try:
                result = self._svc.register(
                    data.get("username", "").strip(),
                    data.get("email", "").strip(),
                    data.get("password", "").strip(),
                )
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        @bp.route("/login", methods=["POST"])
        def login():
            data = request.get_json() or {}
            try:
                result = self._svc.login(
                    data.get("username", ""),
                    data.get("password", ""),
                )
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        @bp.route("/me", methods=["GET"])
        @login_required
        def me():
            return jsonify({
                "user": {
                    "id": g.user.id,
                    "username": g.user.username,
                    "email": g.user.email,
                    "role": g.user.role
                }
            })
# =====================================================
# EXPORTS
# =====================================================
_auth_service = AuthService(_jwt_service)
_auth_blueprint = AuthBlueprint(_auth_service)

auth_bp = _auth_blueprint.blueprint
login_required = login_required


