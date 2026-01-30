# khu vực bàn cờ
from constants import WHITE, BLACK, EMPTY


# định nghĩa lớp bàn cờ
class Board:
    # self.board = [
    #    ['.', '.', '.', '.', '.', '.', '.', '.'],
    #    ['.', '.', '.', '.', '.', '.', '.', '.'],
    #    ['.', '.', '.', '.', '.', '.', '.', '.'],
    #    ['.', '.', '.', '.', '.', '.', '.', '.'],
    #    ['.', '.', '.', '.', '.', '.', '.', '.'],
    #    ['.', '.', '.', '.', '.', '.', '.', '.'],
    #    ['.', '.', '.', '.', '.', '.', '.', '.'],
    #    ['.', '.', '.', '.', '.', '.', '.', '.'],
    # ]
    def __init__(self):
        # định nghĩa list of list(có thể gọi là một mảng hai chiều) bàn cờ
        self.board = [
            # ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            # ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            # ['.', '.', '.', '.', '.', '.', '.', '.'],
            # ['.', '.', '.', '.', '.', '.', '.', '.'],
            # ['.', '.', '.', '.', '.', '.', '.', '.'],
            # ['.', '.', '.', '.', '.', '.', '.', '.'],
            # ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            # ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
            ['.', '.', '.', '.', 'r', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', 'K', '.', '.', '.'],

        ]
        # them trạng thái nhập thành của quân vua và xe rook, king
        self.white_king_moved = False
        self.black_king_moved = False
        # kieu dictionnary
        self.white_rook_moved = {'a': False, 'h': False}
        self.black_rook_moved = {'a': False, 'h': False}
        # định nghĩa lượt quân trắng đi trước
        self.turn = WHITE
        # định nghĩa lịch sử các nước đi là một list rỗng
        self.move_history = []

    # hàm hiện thị ra bàn cờ
    def print_board(self):
        # in ra các chữ cái từ a -> h trong bàn cờ vua quốc tế
        print(" a b c d e f g h")
        # duyệt mảng của self.board để in ra các dữ lieu ở trong đó dùng enumrate
        # đê co thể lấy index vì nó trả về [index,value] mục đích giúp row dữ index một cách tiện lợi
        for i, row in enumerate(self.board):
            # in ra các hang 1-> 8 theo hàng và cột sử dụng 8-i đê không đi từ 0-7
            print(f"{8 - i}" + " ".join(row))
        print()

    # hàm lấy quân và kiểm tra màu
    # hàm lấy ví trị hiện tại của quân cờ với chỉ số là r và c biểu tượng cho hàng và
    # cột và nó trả về self.board[r][c] ví dụ nó sẽ tra về như "K" là vua quân trắng
    def get_piece(self, r, c):
        return self.board[r][c]

    # ham kiểm tra là quân trắng sử dụng supler để kiểm chữ hoa
    # nếu là chữ hoa tra vể True
    def is_white(self, piece):
        return piece.isupper()

    # hàm kiểm tra là quân đen sử dụng islower để kiểm tra chữ thường
    def is_black(self, piece):
        return piece.islower()

    # thực hiện các nước đi để thử lưu ý chưa có luật củ thể ở hàm này
    # chỉ giả lập gồm 4 chỉ số chính fr,fc,tr,tc là first row (bắt đầu ở hàng) ,
    # first column (cột bắt đầu), to row (đên cột), to column(đến cột)
    def make_move(self, move):
        # một kiêu tuple ví dụ move là (6,4,4,4) thì nó sẽ gán lần lượt các biến fr=6, fc=4,tr=4,tc=4 một kiểu giải nén
        if len(move) == 5:
            fr, fc, tr, tc, promotion = move
        else:
            fr, fc, tr, tc = move
            promotion = None
        # lấy vị trị hiện tại của quân cờ tương ứng với nơi bắt đâu luôn ví dụ piece[0][0] quân xe
        piece = self.board[fr][fc]
        # cập nhật tranng thại của quân vua(king) khi nhập thành
        if piece == 'K':
            self.white_king_moved = True
        elif piece == 'k':
            self.black_king_moved = True
        # cập nhật trạng thái của quân xe(rook) khi nhập thành
        if piece == 'R':
            if fc == 0:
                self.white_rook_moved['a'] = True
            elif fc == 7:
                self.black_rook_moved['h'] = True
        # sau khi thực hiện nước đi ví dụ đi quân tốt thì nó sẽ
        # thực hiện xóa nước cũ thì nó tương ứng là đổi thành dấu chấm
        self.board[fr][fc] = EMPTY
        # them phong quan o day sau khi đi thuc hien cập nhật nước cờ mới tr,tc để hiện thị sau khi đi
        if promotion:
            if self.is_white(piece):
                self.board[tr][tc] = promotion.upper()
            else:
                self.board[tr][tc] = promotion.lower()
        else:
            self.board[tr][tc] = piece
        # lưu lịch sử nước cờ vừa đi bằng phương thưc append mảng thêm vào
        self.move_history.append(move)
        # đổi lượt đi giữa quân trắng và quân đen sử dụng toán tử 3 ngôi
        self.turn = BLACK if self.turn == WHITE else WHITE

    # Việc tiếp theo cần làm tình ra cách sinh nước đi hop le :) generate_pseudo_move
    # Hàm sinh nước đi hợp lệ cho quân tốt Pawn(Tốt) hàm gồm self chỉ số hàng c(column) và chỉ số hàng r(row)
    # Mục đích của hàm sẽ là đưa nước đi phù cho quân trắng tiến ăn
    def generate_pawn_moves(self, r, c):
        # khởi tạo mảng các nước di chuyển cua quân tốt giá trị rỗng
        moves = []
        # lấy vị trí hiện tại cảu quân cờ (ở đây có thể là quân Tốt)
        piece = self.board[r][c]
        # Kiểm tra có phải quân tốt trắng không
        if piece == 'P':
            # Đi thang 1 ô theo luật cờ vua nếu chỉ số hàng r >= 0 và vị trị của bàn cờ hieenj tại
            # là dấu chấm thì nó tiến len 1 ô có the di hai ô nếu muốn
            if r - 1 >= 0 and self.board[r - 1][c] == EMPTY:
                # thêm vào mảng di chuyển move của quân này quân trắng sẽ giảm 1 va co the phong quan
                if r - 1 == 0:
                    for p in ['Q', 'R', 'B', 'N']:
                        moves.append((r, c, r - 1, c, p))
                else:
                    moves.append((r, c, r - 1, c))
                # di chuyển 2 ô nếu là hàng đầu kiểm tra nếu r==6 và vị trị hiện tại của quân
                # cờ hàng thứ 2 mang dấu chấm
                if r == 6 and self.board[r - 2][c] == EMPTY:
                    moves.append((r, c, r - 2, c))
            # Ăn Chéo quân nếu hợp lệ điều kiện kiểm tra sẽ là c-1 và r-1 >=0 trường hợp ben trái
            if r - 1 >= 0 and c - 1 >= 0 and self.is_black(self.board[r - 1][c - 1]):
                if r - 1 == 0:
                    for p in ['Q', 'R', 'B', 'N']:
                        moves.append((r, c, r - 1, c - 1, p))
                else:
                    moves.append((r, c, r - 1, c - 1))
            # Ăn chéo quân trường hợp bên phải
            if r - 1 >= 0 and c + 1 < 8 and self.is_black(self.board[r - 1][c + 1]):
                if r - 1 == 0:
                    for p in ['Q', 'R', 'B', 'N']:
                        moves.append((r, c, r - 1, c + 1, p))
                else:
                    moves.append((r, c, r - 1, c + 1))
        # trường hợp nó là quân đen tương tự với quân trắng nhưng đảo ngược lại
        elif piece == 'p':
            # đi thẳng 1 ô
            if r + 1 < 8 and self.board[r + 1][c] == EMPTY:
                # neu len hang thi phong quan
                if r + 1 == 7:
                    # duyet lap cac quan muon phong
                    for p in ['Q', 'R', 'B', 'N']:
                        moves.append((r, c, r + 1, c, p))
                else:
                    moves.append((r, c, r + 1, c))
                # di len hai o neu muon
                if r == 1 and self.board[r + 2][c] == EMPTY:
                    moves.append((r, c, r + 2, c))
            if r + 1 < 8 and c - 1 >= 0 and self.is_white(self.board[r + 1][c - 1]):
                if r + 1 == 7:
                    for p in ['Q', 'R', 'B', 'N']:
                        moves.append((r, c, r + 1, c - 1, p))
                else:
                    moves.append((r, c, r + 1, c - 1))
            if r + 1 < 8 and c + 1 < 8 and self.is_white(self.board[r + 1][c + 1]):
                if r + 1 == 7:
                    for p in ['Q', 'R', 'B', 'N']:
                        moves.append((r, c, r + 1, c + 1, p))
                else:
                    moves.append((r, c, r + 1, c + 1))
        return moves

    # tiếp theo hàm sinh nước đi cho quân mã
    def generate_knight_moves(self, r, c):
        # khoi tao mảng di chuyển của quan mã
        moves = []
        # lấy vị trí hiện tại của quân cờ
        piece = self.board[r][c]
        # kiểm tra có phải quân mã không nếu không thì không làm gì hết
        if piece not in ('N', 'n'):
            return moves
        # xác định màu quân mã vì sở hưu logic ngắn gọn hơn quân tốt thì quân mã khá giông
        # nhau 8 nước đi không bị chặn  và nhảy
        is_white_knight = piece == "N"
        # 8 hướng đi của quân mã
        directions = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1)
        ]
        # dùng vòng lặp để thay thế 8 cái if cho một quân mã bằng cách duyệt dr và dc đó các chỉ số của
        # quân mã của 8 hướng đi nc và nr và nước đi mới của quân mã sau khi cộng lại các cột va hàng mới
        for dr, dc in directions:
            nr = r + dr
            nc = c + dc
            # kiểm tra không ra ngoài bàn cờ
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = self.board[nr][nc]
                # ô trống đi được
                if target == EMPTY:
                    moves.append((r, c, nr, nc))
                # ăn quân khác màu
                elif is_white_knight and self.is_black(target):
                    moves.append((r, c, nr, nc))
                elif not is_white_knight and self.is_white(target):
                    moves.append((r, c, nr, nc))
        return moves

    # hàm sinh nước đi cho quân tượng
    def generate_bishop_moves(self, r, c):
        # khởi tạo các nước quân tượng có thể đi là hàm rỗng
        moves = []
        # lấy vị trị hiện tại cua quân tượng
        piece = self.board[r][c]
        # không phải quân tượng thì không làm gì hết
        if piece not in ('B', 'b'):
            return moves
        # gán biến phân biệt là quân đen hay trang bây giờ đang là trăng sẽ trả về true
        is_white_bishop = piece == "B"
        # 4 hướng đi của quân tượng
        directions = [
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1)
        ]
        # duyệt từng hướng giong luật quân mã nhưng khác là duyệt while thai vì if
        for dr, dc in directions:
            nr = r + dr
            nc = c + dc
            # duyet nằm trong vi đi từng nước một
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = self.board[nr][nc]
                # nếu là dấu chấm trên ma trận thì được đi
                if target == EMPTY:
                    moves.append((r, c, nr, nc))
                # gặp quân đich ăn -> dừng
                elif is_white_bishop and self.is_black(target):
                    moves.append((r, c, nr, nc))
                    break
                elif not is_white_bishop and self.is_white(target):
                    moves.append((r, c, nr, nc))
                    break
                # gặp quân cùng màu dừng
                else:
                    break
                # thực hiện cộng để đi xa hơn + lặp lại đến diều kiện dừng
                nr += dr
                nc += dc
        return moves

    def generate_rook_moves(self, r, c):
        # khởi tạo mảng di chuyển quân xe hiện tại là rỗng
        moves = []
        # lấy vị trí hiện tại của quân xe
        piece = self.board[r][c]
        # không phải quân xe thì không làm gì
        if piece not in ('R', 'r'):
            return moves
        # gán biến phân biệt xe trắng và xe đen
        is_white_rook = piece == "R"
        # 4 hướng đi của quân xe
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]
        # duyệt các nước đi
        for dr, dc in directions:
            nr = r + dr
            nc = c + dc
            # đi tung hướng cho đến khi bị chặn
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = self.board[nr][nc]
                # kiểm tra có phải rỗng nếu không rong thì được đi
                if target == EMPTY:
                    moves.append((r, c, nr, nc))
                # kiểm tra ăn quân va dung lại
                elif is_white_rook and self.is_black(target):
                    moves.append((r, c, nr, nc))
                    break
                elif not is_white_rook and self.is_white(target):
                    moves.append((r, c, nr, nc))
                    break
                # ngược nếu trùng màu thì dừng lại
                else:
                    break
                nr += dr
                nc += dc
        return moves

    # sinh nuoc di cho quan hau
    def generate_queen_moves(self, r, c):
        # khởi tạo moves bằng rỗng
        moves = []
        # lấy vị trí của quân cờ hiện tại
        piece = self.board[r][c]
        # kiểm tra có phải quân hậu nếu không phải thì không làm gì hêt
        if piece not in ('Q', 'q'):
            return moves
        # gán biến để phân biết quân đen và trắng
        is_white_queen = piece == "Q"
        # hướng đi của quân hậu là kết hợp của quân tượng(bishop) quân xe(rook)
        directions = [
            (-1, 0), (1, 0), (0, 1), (0, -1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        # duyệt các quân cờ có nước đi phù hợp
        for dr, dc in directions:
            nr = r + dr
            nc = c + dc
            # duyệt các nước đi đúng hướng cho đến khi bị chan nhu an quân di chuyen dưng rồi lặp lại
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = self.board[nr][nc]
                # kiểm tra có rỗng không nếu rỗng được di chuyen
                if target == EMPTY:
                    moves.append((r, c, nr, nc))
                # kiểm tra ăn quân và dừng lai
                elif is_white_queen and self.is_black(target):
                    moves.append((r, c, nr, nc))
                    break
                elif not is_white_queen and self.is_white(target):
                    moves.append((r, c, nr, nc))
                    break
                # nếu quân cùng màu thì dừng lại
                else:
                    break
                nr += dr
                nc += dc
        return moves

    # hàm di chuyển của quân vua
    def generate_king_moves(self, r, c):
        # khởi tạo một mảng di chuyển quân rỗng
        moves = []
        # lấy ví trí hiện tại của quân
        piece = self.board[r][c]
        # kiểm tra nó có phải quân vua không
        if piece not in ('K', 'k'):
            return moves
        # gán biến phân biệt quân đen trắng
        is_white_king = piece == 'K'
        # 8 hướng đi của quân vua
        directions = [
            (-1, -1), (1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        # duyệt quân các hướng đi hợp lý của quân vua
        for dr, dc in directions:
            nr = r + dr
            nc = c + dc
            # kiểm tra ở trong phạm vi
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = self.board[nr][nc]
                # kiểm tra di chuyển hợp lệ
                if target == EMPTY:
                    moves.append((r, c, nr, nc))
                # kiểm tra ăn quân
                elif is_white_king and self.is_black(target):
                    moves.append((r, c, nr, nc))
                # ngược lại
                elif not is_white_king and self.is_white(target):
                    moves.append((r, c, nr, nc))
        # nhập thành
        if piece == 'K':
            moves.extend(self.generate_castling_moves_w(r, c))
        elif piece == 'k':
            moves.extend(self.generate_castling_moves_b(r, c))
        return moves

    # xây dựng phần chiếu tương
    # hàm tìm quân vua trên bàn cờ truyền màu của quân cờ ví dụ như trắng hoặc đen
    def find_king(self, color):
        # gán biến bằng chữ in hoa và in thường tượng trưng cho quân đen và quân trắng
        king = 'K' if color == WHITE else 'k'
        # duyệt hai vòng lặp trong mảng tương ứng với mảng hai chiều nhằm mục dich tìm hàng và cột
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king:
                    return r, c
        return None

    # hàm gọi luật đi từ quân tốt xe tượng hậu mã vua
    def generate_piece_moves(self, r, c):
        # lây vị trí hiện tại quân cờ
        piece = self.board[r][c]
        # nếu thuộc quân tốt trắng đen thì gọi luat di chuyển tốt
        if piece in ('P', 'p'):
            return self.generate_pawn_moves(r, c)
        # nếu thuộc quân mã thì gọi luật của nó
        if piece in ('N', 'n'):
            return self.generate_knight_moves(r, c)
        # nếu là quân xe thì gọi luật của nó
        if piece in ('R', 'r'):
            return self.generate_rook_moves(r, c)
        # nếu là quân hậu thì gọi luật của nó
        if piece in ('Q', 'q'):
            return self.generate_queen_moves(r, c)
        # nếu là quân tượng thì gọi luật của nó
        if piece in ('B', 'b'):
            return self.generate_bishop_moves(r, c)
        # nếu là quân vua thì gọi luật của nó
        if piece in ('K', 'k'):
            return self.generate_king_moves(r, c)
        return []

    # Liệt kê tất cả các nước đi của quân trắng hoặc đen
    def generate_all_pseudo_moves(self, color):
        # khởi tạo một mảng chứa tất cả các nước đi của bên trăng hoặc đen
        moves = []
        # duyệt hai vòng lặp tượng trưng với cột và hàng trên bàn cờ
        for r in range(8):
            for c in range(8):
                # vị trí hiện tại của quân cờ là gì và đang ở đâu
                piece = self.board[r][c]
                # nếu la dấu chấm thì bỏ qua vì không sinh được nuoc đi
                if piece == EMPTY:
                    continue
                # neu thuộc tập hợp quân trăng và quan co hiên tai là trắng thì gọi luật phù hợp
                if color == WHITE and self.is_white(piece):
                    # cộng hết tất cả nước đi lưu vào mảng
                    moves += self.generate_piece_moves(r, c)
                elif color == BLACK and self.is_black(piece):
                    moves += self.generate_piece_moves(r, c)
        return moves

    # hàm kiểm tra chiếu tướng
    def is_in_check(self, color):
        # tìm quân vua
        king_pos = self.find_king(color)
        # kiem tra quan minh va dối thủ
        opponent = BLACK if color == WHITE else WHITE
        for move in self.generate_all_pseudo_moves(opponent):
            tr, tc = move[2], move[3]
            if (tr, tc) == king_pos:
                return True
        return False

    # lọc nước đi hợp lệ
    # quan trọng vì nó Đi thử -> kiểm tra -> quay lại như cu
    def undo_move(self):
        move = self.move_history.pop()
        # nếu là quan muốn phong
        if len(move) == 5:
            fr, fc, tr, tc, promotion = move
            pawn = 'P' if promotion.isupper() else 'p'
            self.board[tr][tc] = EMPTY
            self.board[fr][fc] = pawn
        # nước đi bình thuong
        else:
            fr, fc, tr, tc = move
            piece = self.board[tr][tc]
            self.board[tr][tc] = EMPTY
            self.board[fr][fc] = piece
        # đổi lượt
        self.turn = BLACK if self.turn == WHITE else WHITE

    # Sinh nước đi hơp lệ mục đích tìm ra quân chiếu và lọc các nuoc đi hợp lệ không bị chiếu
    # không để cho vua của mình bị chiếu sau khi đi
    def generate_legal_moves(self, r, c):
        # khởi tạo mảng các nước đi hợp lệ là rỗng
        legal_moves = []
        # lấy vị trí hiện tại của quân cờ
        piece = self.board[r][c]
        # gán màu để đảo chiều
        color = WHITE if self.is_white(piece) else BLACK
        # sinh ra toàn bộ nước đi hợp lệ
        pseudo_moves = self.generate_piece_moves(r, c)
        # duyệt các nước đi trong vòng lặp
        for move in pseudo_moves:
            # tạo ra các di chuyen hợp lệ
            self.make_move(move)
            # nêu không bị chiếu thì thêm vào mảng nước đi hợp lệ
            if not self.is_in_check(color):
                legal_moves.append(move)
            # quay lại nước trước đó
            self.undo_move()
        return legal_moves

    # nhập thành
    # kiểm tra nhập thành có bị chieu trươc khi nhập thành không
    def is_square_attacked(self, r, c, by_color):
        for move in self.generate_all_pseudo_moves(by_color):
            # đây chính là hai phần tử row col target của quân địch
            if move[2] == r and move[3] == c:
                return True
            return False

    # hàm sinh nước đi cho nhập thành quân trắng
    def generate_castling_moves_w(self, r, c):
        moves = []
        # quân cơ hiện tại
        piece = self.board[r][c]
        # kiểm tra nếu là quân trắng
        if piece == 'K':
            # nếu quân vua trắng đã đi rồi thì không làm gì cả
            if self.white_king_moved:
                return moves
            opponent = BLACK
            # nhập thành canh vua
            if not self.white_rook_moved['h']:
                if self.board[7][5] == EMPTY and self.board[7][6] == EMPTY:
                    if not self.is_square_attacked(7, 4, opponent) and \
                            not self.is_square_attacked(7, 5, opponent) and \
                            not self.is_square_attacked(7, 6, opponent):
                        moves.append((7, 4, 7, 6, 'castle'))
            # nhâp thành cánh hậu
            if not self.white_rook_moved['a']:
                if self.board[7][1] == EMPTY and self.board[7][2] == EMPTY and self.board[7][3] == EMPTY:
                    if not self.is_square_attacked(7, 4, opponent) and \
                            not self.is_square_attacked(7, 3, opponent) and \
                            not self.is_square_attacked(7, 2, opponent):
                        moves.append((7, 4, 7, 2, 'castle'))
        return moves

    # dành cho quân đen
    def generate_castling_moves_b(self, r, c):
        moves = []
        piece = self.board[r][c]
        if piece == 'k':
            if self.black_king_moved:
                return moves
            opponent = WHITE
            if not self.black_rook_moved['h']:
                if self.board[0][5] == EMPTY and self.board[0][6] == EMPTY:
                    if not self.is_square_attacked(0, 4, opponent) and \
                       not self.is_square_attacked(0, 5, opponent) and \
                       not self.is_square_attacked(0, 6, opponent):
                        moves.append((0, 4, 0, 6, 'castle'))
                if not self.black_rook_moved['a']:
                    if self.board[0][1] == EMPTY and self.board[0][2] == EMPTY and self.board[0][3]:
                        if not self.is_square_attacked(0, 4, opponent) and \
                           not self.is_square_attacked(0, 3, opponent) and \
                           not self.is_square_attacked(0, 2, opponent):
                            moves.append((0, 4, 0, 2, 'castle'))
        return moves
