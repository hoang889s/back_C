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




