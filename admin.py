from functools import wraps
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from database import SessionLocal
from models import User, UserRole

class AdminService:
    # ket noi database
    def get_session(self):
        return SessionLocal()
    # mang list user bat dau 1 va ket thuc 20
    def list_users(self,page:int=1,per_page:int = 20)->dict:
        # khoi dong session
        session = self.get_session()
        # thanh cong
        try:
            # dem so luong User da truy van co bao nhieu user
            total = session.query(User).count()
            # thuc hien truy van bang id 
            users =(
                session.query(User).order_by(User.id).offset((page - 1)*per_page).limit(per_page).all()
            )
            # truy van xong tra ve object mot user
            return{
                "total":total,
                "page":page,
                "per_page":per_page,
                "users":[self._serialize(u) for u in users],
            }
        # cuoi dong session
        finally:
            session.close()
    # lay du lieu user
    def get_user(self,user_id:int)->dict:
        # khoi dong session
        session = self.get_session()
        # thanh cong
        try:
            # truy van thong tin user bang id tu id truyen tu ham
            user = session.query(User).filter(User.id == user_id).first()
            # neu khong phai user 
            if not user:
                # thong bao khong tim thay user
                raise LookupError("Không tìm thấy user")
            return self._serialize(user,full=True)
        finally:
            # dong session
            session.close()
    # hàm cập nhật thông tin user
    def update_user(self,user_id:int,data:dict)->dict:
        # bắt đầu session
        session = self.get_session()
        try:
            # truy van thong tin user bang id tu id truyen tu ham
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise LookupError("Không tìm thấy user")
            # nếu username có trong data thì 
            if "username" in data:
                # strip() loại bỏ khoảng trắng đầu và cuối
                new_name = data["username"].strip()
                # kiểm tra đổi có hợp lệ không
                if len(new_name)<3:
                    raise ValueError("username phải có ít nhất 3 ký tự")
                # kiểm tra trùng trừ chính nó trước đó
                conflict = (
                     session.query(User).filter(User.username == new_name, User.id != user_id).first()
                )
                # nếu đúng
                if conflict:
                    raise LookupError("__conflict__username__")
                # tạo username mới
                user.username = new_name
            # kiểm tra email
            if "email" in data:
                # lấy email bỏ khoảng trắng và bỏ chữ in hoa
                new_email = data["email"].strip().lower()
                # kiểm có @ không 
                if "@" not in new_email:
                    raise ValueError("email phải có @")
                # kiểm tra trùng
                conflict = (
                    session.query(User).filter(User.email == new_email, User.id != user_id).first()
                )
                if conflict:
                    raise LookupError("__conflict__email__")
                # trả về email mới
                user.email = new_email
            # kiểm tra mật khẩu
            if "password" in data:
                # loại bỏ khoảng trắng
                pw = data["password"].strip()
                # kiểm tra độ dài dưới 6
                if len(pw)<6:
                    raise ValueError("password phải có ít nhất 6 ký tự")
                # hash mật khẩu mới
                user.password_hash = generate_password_hash(pw)
            # kiểm tra role quyền
            if "role" in data:
                try:
                    # trao quyền 
                    user.role = UserRole(data[  "role"])
                except ValueError:
                    raise ValueError(f"role không hợp lệ, chỉ chấp nhận: {[r.value for r in UserRole]}")
            session.commit()
            # tải lại quá trình update
            session.refresh(user)

            return self._serialize(user, full=True)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    # hàm xóa delelte
    def delete_user(self,user_id:int,current_admin_id:int)->None:
        # kiểm tra id của admin
        if user_id == current_admin_id:
            raise PermissionError("Không thể tự xóa tài khoản admin của chính mình")
        # mở session
        session = self.get_session()
        try:
            # truy vấn
            user = session.query(User).filter(User.id == user_id).first()
            # kiểm tra nếu không phải user
            if not user:
                raise LookupError("Không tìm thấy user")
            # nếu không có gì thì xóa user đi
            session.delete(user)
            # commit lại
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    # phương thức này này là phương thức tĩnh không cần self
    @staticmethod
    # đôi chuyển object User (SQLAlchemy model) thành dictionary (dict) 
    def _serialize(user:User,full:bool = False)->dict:
        # tạo base chứa thông tin cơ bản của user
        base = {
            "id":user.id,
            "username":user.username,
            "email":user.email,
            "role":user.role.value,
        }
        # nếu full đúng thì thếm thông tin thêm vào base
        if full and hasattr(user,"created_at"):
            base["created_at"] = user.created_at.isoformat() if user.created_at else None
        # trả về base
        return base
# gom các api admin lại tách riêng logic của nó 
# Tách riêng logic admin khỏi phần khác (clean architecture)
class AdminBlueprint:
    def __init__(self,admin_service:AdminService|None=None,jwt_service =None,url_prefix:str="/admin"):
        # import muộn tránh circular tránh cho cả hai file import lẫn nhau
        from auth import _jwt_service as shared_jwt
        self._svc = admin_service or AdminService()
        self._jwt = jwt_service or shared_jwt
        self.blueprint = Blueprint("admin",__name__,url_prefix = url_prefix)
        self._register_routes()
    # Middleware: phải login VÀ phải là admin
    # là một decorator (middleware) dùng để bảo vệ route yêu cầu quyền admin.
    def admin_required(self,f):
        @wraps(f)
        def decorated(*args,**kwargs):
            header = request.headers.get("Authorization","")
            # nếu chuỗi header không có Bearer
            if not header.startswith("Bearer "):
                # đã đăng nhập nhưng không xác thực được
                return jsonify({"status": "error", "message": "Thiếu token xác thực"}), 401
            # bỏ phần đầu lấy phần sau đó
            payload = self._jwt.decode(header[7:])
            if not payload:
                return jsonify({"status": "error", "message": "Token không hợp lệ hoặc hết hạn"}), 401
            # kiểm tra quyền admin trong DB (không tin tuyệt đối vào payload)
            # --- DEBUG TẠM ---
            print(">>> payload đầy đủ:", payload)
            print(">>> payload['sub'] :", payload.get("sub"), type(payload.get("sub")))
            # --- HẾT DEBUG ---

            from database import SessionLocal
            # bắt đầu phiên mới
            session = SessionLocal()
            try:
                user = session.query(User).filter(User.id == payload["sub"]).first()
                if not user or user.role != UserRole.ADMIN:
                    # 403 fobiden đã xác thực nhưng không đủ quyền
                    return jsonify({"status": "error", "message": "Không có quyền admin"}), 403
                # lấy payload
                request.current_user = payload
                # lấy id
                request.current_user_id = user.id
            finally:
                session.close()
            return f(*args, **kwargs)
        return decorated
    # đăng ký route
    def _register_routes(self):
        bp = self.blueprint
        # GET /admin/users?page=1&per_page=20
        @bp.route("/users", methods=["GET"])
        @self.admin_required
        def list_users():
            # phân trang lấy danh sách user
            try:
                # đầu trang
                page = int(request.args.get("page", 1))
                # trang cuối
                per_page = int(request.args.get("per_page", 20))
                # kết quả
                result   = self._svc.list_users(page, per_page)
                # thành công 200
                return jsonify({"status": "ok", **result}), 200
            except Exception as e:
                # lỗi server 500 ở admin
                return jsonify({"status": "error", "message": f"Lỗi server(từ admin _register_routes): {e}"}), 500
        # GET /admin/users/<id>
        @bp.route("/users/<int:user_id>", methods=["GET"])
        @self.admin_required
        # lấy dữ liệu user
        def get_user(user_id):
            try:
                # tìm id users
                user = self._svc.get_user(user_id)
                # thành công
                return jsonify({"status": "ok", "user": user}), 200
            except LookupError as e:
                # 404 không tìm thấy tài nguyên
                return jsonify({"status": "error", "message": f"Lỗi từ get_user(từ admin _register_routes):{str(e)}"}), 404
            except Exception as e:
                # lỗi server 500 ở admin
                return jsonify({"status": "error", "message": f"Lỗi server(từ admin _register_routes): {e}"}), 500
        # cập nhât toàn bộ dữ liệu
        # PUT /admin/users/<id>
        @bp.route("/users/<int:user_id>", methods=["PUT"])
        @self.admin_required
        def update_user(user_id):
            # lấy dữ liệu hoặc là rỗng
            data = request.get_json(silent=True) or {}
            try:
                # lấy ra user
                user = self._svc.update_user(user_id, data)
                # thành công 200
                return jsonify({"status": "ok", "user": user}), 200
            except ValueError as e:
                # bad required 400 sai request
                return jsonify({"status": "error", "message": f"Lỗi từ update_user(từ admin _register_routes):{str(e)}"}), 400
            except PermissionError as e:
                # fobiden 403 không đủ quyền
                return jsonify({"status": "error", "message": str(e)}), 403
            except LookupError as e:
                msg = str(e)
                if "__conflict__" in msg:
                    field = msg.split("__")[2]
                    # mã 409 conflig xung đột trùng dữ liệu
                    return jsonify({"status": "error", "message": f"{field} đã tồn tại"}), 409
                return jsonify({"status": "error", "message": msg}), 404
            except Exception as e:
                # lỗi server
                return jsonify({"status": "error", "message": f"Lỗi server: {e}"}), 500
        # xoa du lieu
        @bp.route("/users/<int:user_id>", methods=["DELETE"])
        @self.admin_required
        def delete_user(user_id):
            try:
                # xoa du lieu
                self._svc.delete_user(user_id, request.current_user_id)
                # xoa thanh cong
                return jsonify({"status": "ok", "message": "Đã xóa user thành công"}), 200
            except PermissionError as e:
                # khong co quyen xoa 403
                return jsonify({"status": "error", "message": str(e)}), 403
            except LookupError as e:
                return jsonify({"status": "error", "message": str(e)}), 404
            except Exception as e:
                # loi server
                return jsonify({"status": "error", "message": f"Lỗi server: {e}"}), 500
# export 
_admin_blueprint = AdminBlueprint()
admin_bp         = _admin_blueprint.blueprint
        




        
    
    