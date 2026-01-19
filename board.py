# khu vực bàn cờ
from constants import WHITE,BLACK,EMPTY
# định nghĩa lớp bàn cờ
class Board:
    def __init__(self):
        # định nghĩa list of list(có thể gọi là một mảng hai chiều) bàn cờ
        self.board =[
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
        ]
        # định nghĩa lượt quân trắng đi trước
        self.turn = WHITE
        # định nghĩa lịch sử các nước đi là một list rỗng
        self.move_history = []
    # hàm hiện thị ra bàn cờ
    def print_board(self):
        # in ra các chữ cái từ a -> h trong bàn cờ vua quốc tế
        print(" a b c d e f g h")
        # duyệt mảng của self.board để in ra các dữ lieu ở trong đó dùng enumrate đê co thể lấy index vì nó trả về [index,value] mục đích giúp row dữ index một cách tiện lợi
        for i, row in enumerate(self.board):
            # in ra các hang 1-> 8 theo hàng và cột sử dụng 8-i đê không đi từ 0-7
            print(f"{8-i}"+" ".join(row))
        print()
    # hàm lấy quân và kiểm tra màu
    # hàm lấy ví trị hiện tại của quân cờ với chỉ số là r và c biểu tượng cho hàng và cột và nó trả về self.board[r][c] ví dụ nó sẽ tra về như "K" là vua quân trắng
    def get_piece(self, r, c):
        return self.board[r][c]
    #ham kiểm tra là quân trắng sử dụng supler để kiểm chữ hoa nếu là chữ hoa tra vể True
    def is_white(self, piece):
        return piece.isupper()
    # hàm kiểm tra là quân đen sử dụng islower để kiểm tra chữ thường
    def is_black(self, piece):
        return  piece.islower()
    # thực hiện các nước đi để thử lưu ý chưa có luật củ thể ở hàm này chỉ giả lập gồm 4 chỉ số chính fr,fc,tr,tc là first row (bắt đầu ở hàng) , first column (cột bắt đầu), to row (đên cột), to column(đến cột)
    def make_move(self, move):
        # một kiêu tuple ví dụ move là (6,4,4,4) thì nó sẽ gán lần lượt các biến fr=6, fc=4,tr=4,tc=4 một kiểu giải nén
        fr,fc,tr,tc = move
        # lấy vị trị hiện tại của quân cờ tương ứng với nơi bắt đâu luôn ví dụ piece[0][0] quân xe
        piece = self.board[fr][fc]
        # sau khi thực hiện nước đi ví dụ đi quân tốt thì nó sẽ thực hiện xóa nước cũ thì nó tương ứng là đổi thành dấu chấm
        self.board[fr][fc] = EMPTY
        # sau khi đi thuc hien cập nhật nước cờ mới tr,tc để hiện thị sau khi đi
        self.board[tr][tc] = piece
        # lưu lịch sử nước cờ vừa đi bằng phương thưc append mảng thêm vào
        self.move_history.append(move)
        # đổi lượt đi giữa quân trắng và quân đen sử dụng toán tử 3 ngôi
        self.turn = BLACK if self.turn == WHITE else WHITE
    # Việc tiếp theo cần làm tình ra cách sinh nước đi hop le :) generate_pseudo_move
    # Hàm sinh nước đi hợp lệ cho quân tốt Pawn(Tốt) hàm gồm self chỉ số hàng c(column) và chỉ số hàng r(row)
    # Mục đích của hàm sẽ là đưa nước đi phù cho quân trắng tiến ăn
    def generate_pawn_moves(self,r,c):
        # khởi tạo mảng các nước di chuyển cua quân tốt giá trị rỗng
        moves = []
        # lấy vị trí hiện tại cảu quân cờ (ở đây có thể là quân Tốt)
        piece = self.board[r][c]
        # Kiểm tra có phải quân tốt trắng không
        if piece == 'P':
            # Đi thang 1 ô theo luật cờ vua nếu chỉ số hàng r >= 0 và vị trị của bàn cờ hieenj tại là dấu chấm thì nó tiến len 1 ô có the di hai ô nếu muốn
            if r-1>=0 and self.board[r-1][c]==EMPTY:
                # thêm vào mảng di chuyển move của quân này quân trắng sẽ giảm 1
                moves.append((r,c,r-1,c))
                # di chuyển 2 ô nếu là hàng đầu kiểm tra nếu r==6 và vị trị hiện tại của quân cờ hàng thứ 2 mang dấu chấm
                if r==6 and self.board[r-2][c]==EMPTY:
                    moves.append((r,c,r-2,c))
            # Ăn Chéo quân nếu hợp lệ điều kiện kiểm tra sẽ là c-1 và r-1 >=0 trường hợp ben trái
            if r-1>=0 and c-1>=0:
                # neu là quân đen thì đươc ăn
                if self.is_black(self.board[r-1][c-1]):
                    moves.append((r,c,r-1,c-1))
            # Ăn chéo quân trường hợp bên phải
            if r-1>=0 and c+1<8:
                # kiểm nếu là quân đen ăn
                if self.is_black(self.board[r-1][c+1]):
                    moves.append((r,c,r-1,c+1))
        # trường hợp nó là quân đen tương tự với quân trắng nhưng đảo ngược lại
        elif piece== 'p':
            # đi thẳng 1 ô
            if r+1<8 and self.board[r+1][c]==EMPTY:
                moves.append((r,c,r+1,c))
                if r==1 and self.board[r+2][c]==EMPTY:
                    moves.append((r,c,r+2,c))
            if r+1<8 and c-1>=0:
                if self.is_white(self.board[r+1][c-1]):
                    moves.append((r,c,r+1,c-1))
            if r+1<8 and c+1<8:
                if self.is_white(self.board[r+1][c+1]):
                    moves.append((r,c,r+1,c+1))
        return moves
    # tiếp theo hàm sinh nước đi cho quân mã
    def generate_knight_moves(self,r,c):
        # khoi tao mảng di chuyển của quan mã
        moves =[]
        # lấy vị trí hiện tại của quân cờ
        piece = self.board[r][c]
        # kiểm tra có phải quân mã không nếu không thì không làm gì hết
        if piece not in ('N','n'):
            return moves
        # xác định màu quân mã vì sở hưu logic ngắn gọn hơn quân tốt thì quân mã khá giông nhau 8 nước đi không bị chặn  và nhảy
        is_white_knight = piece == "N"
        # 8 hướng đi của quân mã
        directions = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1)
        ]
        # dùng vòng lặp để thay thế 8 cái if cho một quân mã bằng cách duyệt dr và dc đó các chỉ số của quân mã của 8 hướng đi nc và nr và nước đi mới của quân mã sau khi cộng lại các cột va hàng mới
        for dr,dc in directions:
            nr = r + dr
            nc = c + dc
            # kiểm tra không ra ngoài bàn cờ
            if 0<=nr<8 and 0 <=nc<8:
                target=self.board[nr][nc]
                # ô trống đi được
                if target == EMPTY:
                    moves.append((r,c,nr,nc))
                # ăn quân khác màu
                elif is_white_knight and self.is_black(target):
                    moves.append((r,c,nr,nc))
                elif not is_white_knight and self.is_white(target):
                    moves.append((r,c,nr,nc))
        return moves
    # hàm sinh nước đi cho quân tượng
    def generate_bishop_moves(self,r,c):
        # khởi tạo các nước quân tượng có thể đi là hàm rỗng
        moves =[]
        # lấy vị trị hiện tại cua quân tượng
        piece=self.board[r][c]
        # không phải quân tượng thì không làm gì hết
        if piece not in ('B','b'):
            return moves
        #gán biến phân biệt là quân đen hay trang bây giờ đang là trăng sẽ trả về true
        is_white_bishop =piece=="B"
        # 4 hướng đi của quân tượng
        directions = [
            (-1,-1),# trái lên
            (-1,1),# lên phải
            (1,-1),# trái xuống
            (1,1)# phải xuống
        ]
        # duyệt từng hướng giong luật quân mã nhưng khác là duyệt while thai vì if
        for dr,dc in directions:
            nr = r+dr
            nc = c+dc
            # duyet nằm trong vi đi từng nước một
            while 0<=nr<8 and 0<=nc<8:
                target = self.board[nr][nc]
                # nếu là dấu chấm trên ma trận thì được đi
                if target == EMPTY:
                    moves.append((r,c,nr,nc))
                # gặp quân đich ăn -> dừng
                elif is_white_bishop and self.is_black(target):
                    moves.append((r,c,nr,nc))
                    break
                elif not is_white_bishop and  self.is_white(target):
                    moves.append((r,c,nr,nc))
                    break
                # gặp quân cùng màu dừng
                else :
                    break
                # thực hiện cộng để đi xa hơn + lặp lại đến diều kiện dừng
                nr += dr
                nc += dc
        return  moves
    def generate_rook_moves(self,r,c):
        # khởi tạo mảng di chuyển quân xe hiện tại là rỗng
        moves =[]
        # lấy vị trí hiện tại của quân xe
        piece = self.board[r][c]
        # không phải quân xe thì không làm gì
        if piece not in ('R','r'):
            return moves
        # gán biến phân biệt xe trắng và xe đen
        is_white_rook=piece=="R"
        # 4 hướng đi của quân xe
        directions =[
            (-1,0),#lên
            (1,0),#xuống
            (0,-1),# trái
            (0,1)# phải
        ]
        # duyệt các nước đi
        for dr,dc in directions:
            nr = r + dr
            nc= c +dc
            # đi tung hướng cho đến khi bị chặn
            while 0<=nr<8 and 0<=nc<8:
                target = self.board[nr][nc]
                #kiểm tra có phải rỗng nếu không rong thì được đi
                if target==EMPTY:
                    moves.append((r,c,nr,nc))
                # kiểm tra ăn quân va dung lại
                elif is_white_rook and self.is_black(target):
                    moves.append((r,c,nr,nc))
                    break
                elif not is_white_rook and self.is_white(target):
                    moves.append((r,c,nr,nc))
                    break
                # ngược nếu trùng màu thì dừng lại
                else:
                    break
                nr += dr
                nc += dc
        return moves
    # sinh nuoc di cho quan hau
    def generate_queen_moves(self,r,c):
        # khởi tạo moves bằng rỗng
        moves = []
        # lấy vị trí của quân cờ hiện tại
        piece=self.board[r][c]
        # kiểm tra có phải quân hậu nếu không phải thì không làm gì hêt
        if piece not in ('Q','q'):
            return moves
        # gán biến để phân biết quân đen và trắng
        is_white_queen=piece == "Q"
        # hướng đi của quân hậu là kết hợp của quân tượng(bishop) quân xe(rook)
        directions = [
            (-1,0),(1,0),(0,1),(0,-1),
            (-1,-1),(-1,1),(1,-1),(1,1)
        ]
        # duyệt các quân cờ có nước đi phù hợp
        for dr,dc in directions:
            nr = r+dr
            nc = c+dc
            # duyệt các nước đi đúng hướng cho đến khi bị chan nhu an quân di chuyen dưng rồi lặp lại
            while 0<=nr<8 and 0<=nc<8:
                target = self.board[nr][nc]
                # kiểm tra có rỗng không nếu rỗng được di chuyen
                if target==EMPTY:
                    moves.append((r,c,nr,nc))
                # kiểm tra ăn quân và dừng lai
                elif is_white_queen and self.is_black(target):
                    moves.append((r,c,nr,nc))
                    break
                elif not is_white_queen and self.is_white(target):
                    moves.append((r,c,nr,nc))
                    break
                # nếu quân cùng màu thì dừng lại
                else:
                    break
                nr += dr
                nc += dc
        return moves
    # hàm di chuyển của quân vua
    def generate_king_moves(self,r,c):
        # khởi tạo một mảng di chuyển quân rỗng
        moves = []
        # lấy ví trí hiện tại của quân
        piece = self.board[r][c]
        # kiểm tra nó có phải quân vua không
        if piece not in ('K','k'):
            return moves
        # gán biến phân biệt quân đen trắng
        is_white_king= piece == 'K'
        # 8 hướng đi của quân vua
        directions = [
            (-1,1),(1,0),(-1,1),
            (0,-1),(0,1),
            (1,-1),(1,0),(1,1)
        ]
        # duyệt quân các hướng đi hợp lý của quân vua
        for dr,dc in directions:
            nr = r + dr
            nc = c + dc
            # kiểm tra ở trong phạm vi
            if  0<=nr<8 and 0<=nc<8:
                target = self.board[nr][nc]
                # kiểm tra di chuyển hợp lệ
                if target == EMPTY:
                    moves.append((r,c,nr,nc))
                # kiểm tra ăn quân
                elif is_white_king and self.is_black(target):
                    moves.append((r,c,nc,nr))
                # ngược lại
                elif not is_white_king and self.is_white(target):
                    moves.append((r,c,nr,nc))
        return moves














