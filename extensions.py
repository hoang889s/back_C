from flask_socketio import SocketIO

# SocketIO instance dùng chung toàn app
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading"  # an toàn, không cần eventlet/gevent
)