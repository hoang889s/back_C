from flask import Flask
from config import Config
from persistence.database import init_db
from extensions import socketio

# blueprints
from api.auth import auth_bp
from admin import admin_bp
from api.routes import game_bp


from api import sockets
from flask_cors import CORS

import logging
def create_app(config=Config):
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    logging.basicConfig(
        level=logging.DEBUG if config.DEBUG else logging.INFO
    )
    # init socket
    socketio.init_app(app, cors_allowed_origins="*")
    # db
    try:
        init_db()
    except Exception as e:
        print("[DB ERROR]", e)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(game_bp)
    return app
if __name__ == "__main__":
    app = create_app()
    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
    import sys
    print("lỗi ở đây",sys.path)