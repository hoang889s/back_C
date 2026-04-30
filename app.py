from flask import Flask
from config import Config
from persistence.database import init_db
from extensions import socketio

# blueprints
from api.auth import auth_bp
from admin import admin_bp
from api.routes import game_bp

# QUAN TRỌNG: import để register socket events
import api.sockets  

from flask_cors import CORS
import logging


def create_app(config=Config):
    app = Flask(__name__)

    # =============================
    # SECRET KEY (BẮT BUỘC cho session)
    # =============================
    app.config["SECRET_KEY"] = config.SECRET_KEY or "dev-secret-key"

    # =============================
    # CORS (chỉ cần 1 cái thôi)
    # =============================
    CORS(
        app,
        supports_credentials=True,
        origins=["http://localhost:5173"]
    )

    # =============================
    # LOGGING
    # =============================
    logging.basicConfig(
        level=logging.DEBUG if config.DEBUG else logging.INFO
    )

    # =============================
    # SOCKET INIT
    # =============================
    socketio.init_app(
        app,
        cors_allowed_origins=["http://localhost:5173"],
        manage_session=True   # QUAN TRỌNG
    )

    # =============================
    # DB INIT
    # =============================
    try:
        init_db()
        print("[DB] Đã khởi tạo schema thành công.")
    except Exception as e:
        print("[DB ERROR]", e)

    # =============================
    # REGISTER BLUEPRINT
    # =============================
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(game_bp)

    return app


# =============================
# MAIN
# =============================
if __name__ == "__main__":
    app = create_app()
    print("ASYNC MODE:", socketio.async_mode)
    print("📦 DB_URL:", Config.DB_URL)
    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )