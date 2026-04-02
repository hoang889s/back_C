from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import Room, RoomStatus, RoomMode, GameHistory, GameResult
from auth import login_required
from datetime import datetime, timezone
from typing import Optional
import secrets, bcrypt, logging
# không phụ thuộc DB/ request
class RoomHelper:
    # băm mật khẩu
    @staticmethod
    def hash_password(pw:str)->str:
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    # kiểm tra mật khẩu
    @staticmethod
    def check_password(pw:str,hashed:str)->bool:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    # sinh mã cho phòng
    @staticmethod
    def generate_code(db)->str:
        """Sinh mã phòng 8 ký tự duy nhất."""
        while True:
            code = secrets.token_hex(4).upper()
            if not db.query(Room).filter_by(code=code).first():
                return code
    # chuyển sang json
    @staticmethod
    def to_json(room:Room)->dict:

        try:
            host_username = room.host.username if room.host else None
        except:
            host_username = None
        try:
            guest_username = room.guest.username if room.guest else None
        except Exception:
            guest_username = None
        return{
            "id": room.id,
            "code": room.code,
            "mode": room.mode.value if room.mode else None,
            "status": room.status.value if room.status else None,
            "host_color": room.host_color,
            "has_password": room.password_hash is not None,
            "time_limit": room.time_limit,
            "host": {"id": room.host_id, "username": host_username} if room.host_id else None,
            "guest": {"id": room.guest_id, "username":  guest_username} if room.guest_id else None,
            "game_id": room.game_id,
            "created_at": room.created_at.isoformat() if room.created_at else None,
            "started_at": room.started_at.isoformat() if room.started_at else None,
            "ended_at":   room.ended_at.isoformat()   if room.ended_at   else None,
        }
# roommanager
class RoomManager:
    # khởi tạo
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    # mở db
    def _get_db(self):
        return SessionLocal()
    #  helper eager-load host và guest trong session
    @staticmethod
    def _eager_load(room:Room):
        #Truy cập host/guest trong session để SQLAlchemy cache lại, tránh DetachedInstanceError.
        try:
             _ = room.host
        except Exception:
            pass
        try:
             _ = room.guest
        except Exception:
            pass
    # tạo 
    def create(self,host_id:int,mode:str = "pvp",host_color:str="white",password:Optional[str]=None,time_limit:Optional[str]=None,)->Room:
        # mở db
        db = self._get_db()
        try:
            # tạo một phòng mới với các thông tin
            room = Room(
                # sinh mã phòng
                code = RoomHelper.generate_code(db),
                # host id
                host_id = host_id,
                # chế độ
                mode = RoomMode(mode),
                # phe
                host_color = host_color,
                # mật khẩu có thể none
                password_hash = RoomHelper.hash_password(password) if password else None,
                # giới hạn thời gian
                time_limit = time_limit, 
            )
            # thêm 
            db.add(room)
            # thêm cứng vào database 
            db.commit()
            # tải lại
            db.refresh(room)
            # eager-load trước khi đóng session
            self._eager_load(room)
            # ghi log thông báo ở terminal server
            self.logger.info(f"[Room] Tạo phòng {room.code} bởi user {host_id}")
            return room
        finally:
            db.close()
    # Lấy danh sách theo code
    def get_by_code(self,code:str)->Optional[Room]:
        # mở db
        db = self._get_db()
        try:
            # trả về kết quả đầu tiên tìm được hoặc None nếu không tìm thấy
            #return db.query(Room).filter_by(code=code.upper()).first()
            room = db.query(Room).filter_by(code=code.upper()).first()
            if room:
                self._eager_load(room)
                return room
        finally:
            db.close()
    # Danh sách phòng công khai
    def list_public(self,status:str="waiting",mode:Optional[str] = None,limit: int=50)->list[Room]:
        # mở database
        db = self._get_db()
        try:
            # truy vấn status và mật khẩu băm
            q = db.query(Room).filter(Room.password_hash == None,Room.status == RoomStatus(status),)
            # kiểm tra mode có phải pva hoặc pvp không
            if mode in ("pvp","pva"):
                # truy vấn theo mode
                q = q.filter(Room.mode == RoomMode(mode))
            rooms = q.order_by(Room.created_at.desc()).limit(limit).all()
            # eager-load tất cả rooms trước khi đóng session
            for r in rooms:
                self._eager_load(r)
            return rooms
            # trả về toàn dữ liệu truy vấn được với giơi hạn limit săp xếp tăng dần theo ngày tạo
            #return q.order_by(Room.created_at.desc()).limit(limit).all()
        finally:
            db.close()
    # phòng của một user
    def list_by_user(self,user_id:int,limit:int=20)->list[Room]:
        # mở db
        db = self._get_db()
        try:
            rooms = (
                db.query(Room)
                .filter((Room.host_id == user_id) | (Room.guest_id == user_id))
                .order_by(Room.created_at.desc())
                .limit(limit)
                .all()
            )
            for r in rooms:
                self._eager_load(r)
            return rooms
        finally:
            db.close()
    # tham gia phòng sử tuple để không sửa được dữ liệu
    def join(self,code:str,guest_id:int,password:Optional[str] = None)->tuple[Optional[Room], Optional[str]]:
        # Trả về (room, None) nếu thành công, (None, error_message) nếu thất bại.
        # mở database
        db = self._get_db()
        try:
            # truy vấn đơn giản filter_by chỉ có so sánh bằng đưa về kết quả đầu tiên tìm được bởi code ở dạng viết hoa
            room = db.query(Room).filter_by(code=code.upper()).first()
            # kiểm tra nếu không phải phòng thì không toàn tại
            if not room:
                return None, "Phòng không tồn tại"
            # kiểm tra trạng thái phòng
            if room.status != RoomStatus.WAITING:
                return None, "Phòng không còn chỗ trống"
            # kiểm tra mật khẩu phòng
            if room.password_hash and not password:
                return None, "Phòng yêu cầu mật khẩu"
            # kiểm tra có nhập mật khẩu đúng không
            if room.password_hash and not RoomHelper.check_password(password, room.password_hash):
                return None, "Mật khẩu sai"
            # tạo lịch sư ván cơ khi trò chơi bắt đầu
            game = GameHistory(
                # chủ phòng sẽ là màu trắng nếu host_color là màu trắng không sẽ là khách
                white_player_id = room.host_id if room.host_color == "white" else guest_id,
                # tương tự cho màu đen
                black_player_id = guest_id if room.host_color == "white" else room.host_id,
            )
            # lưu tạm chưa db
            db.add(game)
            # có thể roll back để sửa một vài thông tin
            db.flush()
            room.guest_id = guest_id
            room.status = RoomStatus.PLAYING
            room.game_id = game.id
            room.started_at = datetime.now(timezone.utc)
            # sau khi sửa một vài thông tin có thể commit lưu cứng db
            db.commit()
            # tải lại
            db.refresh(room)
            #  eager-load trước khi đóng session
            self._eager_load(room)
            # ghi log để thông báo terminal
            self.logger.info(f"[Room] User {guest_id} vào phòng {room.code}")
            return room,None
        finally:
            db.close()
    # rời phòng
    def leave(self,code:str,user_id:int)->tuple[bool,str]:
        # Trả về (True, message) hoặc (False, error).
        # mở db
        db = self._get_db()
        try:
            # truy vấn đơn giản bằng phép = , truy vấn băng code
            room = db.query(Room).filter_by(code=code.upper()).first()
            if not room:
                return False,"Phòng không tồn tại"
            # nếu là chủ phòng sẽ thay đổi một số thông tin
            if user_id == room.host_id:
                # trạng thái bỏ phòng
                room.status = RoomStatus.ABANDONED
                # kêt thúc vào lúc
                room.ended_at = datetime.now(timezone.utc)
                # ghi log
                self.logger.info(f"[Room] Host rời → phòng {room.code} ABANDONED")
            # nếu là khách
            elif user_id == room.guest_id:
                # gán id khách về None 
                room.guest_id = None
                # đổi trạng thái phòng thành waiting
                room.status = RoomStatus.WAITING
                # đổi game_id
                room.game_id = None
                # ghi log
                self.logger.info(f"[Room] Guest rời → phòng {room.code} về WAITING")
            else:
                return False, "Bạn không ở trong phòng này"
            # lưu cứng database
            db.commit()
            return True,"Đã rời phòng"
        finally:
            db.close()
    # kết thúc ván
    def end(self,code:str,user_id:int,result:str)->tuple[Optional[Room], Optional[str]]:
        # Trả về (room, None) hoặc (None, error).
        # mở db
        db = self._get_db()
        try:
            # truy vấn đơn giản bằng filter_by dựa trên code viết Hoa
            room = db.query(Room).filter_by(code=code.upper()).first()
            # nếu không phải phòng
            if not room:
                return None,"Phòng không tồn tại"
            # kiểm tra có phải chủ hay khách không
            if user_id not in (room.host_id, room.guest_id):
                return None , "Bạn không có quyền kết thúc phòng này"
            # sửa thời điểm
            now = datetime.now(timezone.utc)
            room.status = RoomStatus.FINISHED
            room.ended_at = now
            # nếu đúng là game_id
            if room.game_id:
                # lấy theo get khóa chính primary key
                game = db.query(GameHistory).get(room.game_id)
                if game:
                    # đưa ra kết quả luôn
                    game.result = GameResult(result)
                    game.ended_at = now
            # lưu cứng db
            db.commit()
            # tải lải bảng room
            db.refresh(room)
            # eager-load trước khi đóng session
            self._eager_load(room)
            # ghi log
            self.logger.info(f"[Room] Phòng {room.code} kết thúc, kết quả: {result}")
            return room,None
        finally:
            db.close()
# RoomRoutes  –  chỉ xử lý HTTP: validate input → gọi manager → trả JSON
class RoomRoutes:
    # khởi tạo
    def __init__(self,manager:RoomManager):
        self.manager = manager
        self.logger  = logging.getLogger(self.__class__.__name__)
    # Post /rooms/create
    #@login_required
    def create_room(self):
        current_user = request.current_user
        # dữ liệu tạo phòng không báo lối khi exept slient
        data = request.get_json(silent=True) or {}
        mode = data.get("mode","pvp")
        host_color = data.get("host_color","white")
        password = data.get("password")
        time_limit = data.get("time_limit")
        # kiểm tra mode thuộc pvp or pva không
        if mode not in ("pvp","pva"):
            # trả badrequest 400
            return jsonify({"status": "error", "message": "mode phải là 'pvp' hoặc 'pva'"}), 400
        # tạo dữ liệu phòng RoomRoutes
        room = self.manager.create(
            host_id = current_user.id,
            mode = mode,
            host_color = host_color,
            password = password,
            time_limit = int(time_limit) if time_limit else None,
        )
        
        print("DATA:",data)
        # 201 tạo thành công
        return jsonify({"status": "ok", "room": RoomHelper.to_json(room)}), 201
    # POST /rooms/join
    #@login_required
    def join_room(self):
        current_user = request.current_user
        # dữ liệu tạo phòng không báo lối khi exept slient
        data = request.get_json(silent=True) or {}
        code = data.get("code","").strip()
        password = data.get("password")
        # kiểm tra mã phòng
        if not code:
            # bad req 400
            return jsonify({"status": "error", "message": "Thiếu mã phòng"}), 400
        room, error = self.manager.join(code, current_user.id, password)
        if error:
            # Phân biệt lỗi 404 / 403 / 409
            status_code = (
                404 if "tồn tại" in error else 403 if "mật khẩu" in error.lower() or "sai" in error else 409
            )
            return jsonify({"status": "error", "message": error}), status_code
        # thành công
        return jsonify({"status": "ok", "room": RoomHelper.to_json(room)}), 200
    # GET /rooms/
    #@login_required
    def list_rooms(self):
        request.current_user
        # lấy status, mode
        status_filter = request.args.get("status", "waiting")
        mode_filter = request.args.get("mode")
        try:
            # lấy list_room công khai
            rooms = self.manager.list_public(status=status_filter,mode=mode_filter)
        except ValueError:
            # bad request
            return jsonify({"status": "error", "message": "status không hợp lệ"}), 400
        # thành công
        return jsonify({"status": "ok", "rooms": [RoomHelper.to_json(r) for r in rooms]}), 200
    # GET /rooms/my
    #@login_required
    def my_rooms(self):
        current_user = request.current_user
        # lấy list_public
        rooms = self.manager.list_by_user(current_user.id)
        # thành công
        return jsonify({"status": "ok", "rooms": [RoomHelper.to_json(r) for r in rooms]}), 200
    # GET /rooms/<code>
    #@login_required
    def get_room(self,code):
        request.current_user
        # lấy phòng bằng mã
        room = self.manager.get_by_code(code)
        if not room:
            # dữ liệu không tồn tại 404
            return jsonify({"status": "error", "message": "Không tìm thấy phòng"}), 404
        # thành công
        return jsonify({"status": "ok", "room": RoomHelper.to_json(room)}), 200
    # POST /rooms/<code>/leave
    #@login_required
    def leave_room(self,code):
        current_user = request.current_user
        ok,message = self.manager.leave(code, current_user.id)
        # nếu không ok
        if not ok:
            # 404 không tìm thấy 403 không có quyền
            status_code = 404 if "tồn tại" in message else 403
            return jsonify({"status": "error", "message": message}), status_code
        # thành công
        return jsonify({"status": "ok", "message": message}), 200
    # POST /rooms/<code>/end
    #@login_required
    def end_room(self,code):
        current_user = request.current_user
        data = request.get_json(silent=True) or {}
        result = data.get("result","draw")
        if result not in ("win","loss","draw"):
            # bad request 400
            return jsonify({"status": "error", "message": "result phải là 'win', 'loss' hoặc 'draw'"}), 400
        # tận dụng được tuple
        room,error = self.manager.end(code, current_user.id, result)
        if error:
            status_code = (
                404 if "tồn tại" in error else 403 if "quyền" in error else 409
            )
            return jsonify({"status": "error", "message": error}), status_code
        # thành công
        return jsonify({"status": "ok", "message": "Ván đấu đã kết thúc", "room": RoomHelper.to_json(room)}), 200
# RoomBlueprint  –  kết nối routes vào Flask, đăng ký URL rules
class RoomBlueprint:
    # khởi tạo
    def __init__(self):
        self.manager = RoomManager()
        self.routes = RoomRoutes(self.manager)
        self.blueprint = Blueprint("room", __name__, url_prefix="/rooms")
        self._register()
    #def _register(self):
        #add = self.blueprint.add_url_rule
        #r = self.routes
        #url - endpoint - viewfunc - methos
        #add("/","list_rooms",login_required(r.list_rooms),["GET"])
        #add("/create","create_room",login_required(r.create_room),["POST","OPTIONS"])
        #add("/join","join_room",login_required(r.join_room),["POST","OPTIONS"])
        #add("/my","my_rooms",login_required(r.my_rooms),["GET"])
        #add("/<code>","get_room",login_required(r.get_room),["GET"])
        #add("/<code>/leave","leave_room",login_required(r.leave_room),["POST","OPTIONS"])
        #add("/<code>/end","end_room",login_required(r.end_room),["POST","OPTIONS"])
    def _register(self):
        import functools
        add = self.blueprint.add_url_rule
        r = self.routes
        def wrap(fn):
            #Wrap login_required nhưng giữ __name__ unique theo tên hàm gốc.
            wrapped = login_required(fn)
            # Flask dùng cái này làm endpoint
            #print(login_required(r.join_room).__name__)
            wrapped.__name__ = fn.__name__
            return wrapped
        add("/","list_rooms",wrap(r.list_rooms),methods=["GET"])
        add("/create","create_room",wrap(r.create_room),methods=["POST","OPTIONS"])
        #print(wrap(r.join_room))
        add("/join","join_room",wrap(r.join_room),methods=["POST","OPTIONS"])
        add("/my","my_rooms",wrap(r.my_rooms),methods=["GET"])
        add("/<code>","get_room",wrap(r.get_room),methods=["GET"])
        add("/<code>/leave","leave_room",wrap(r.leave_room),methods=["POST","OPTIONS"])
        add("/<code>/end","end_room",wrap(r.end_room),methods=["POST","OPTIONS"])
        

        
        
# Instance dùng để đăng ký vào app.py
room_bp = RoomBlueprint().blueprint



        


                



