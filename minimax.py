from constants import WHITE, BLACK, EMPTY
# bảng đánh giá thưởng phạt của quân tốt

class Minimax:
    def __init__(self,depth):
        # khoi tao
        self.depth = depth
    # ham gia ban co
    # ham nay danh gia diem so cac quan co
    def evaluate(self, board):
        # khoi tao diem dau tien
        score = 0
        piece_values = {
            'P': 100, 'N': 320, 'B': 330,
            'R': 500, 'Q': 900, 'K': 20000
        }
        for r in range(8):
            for c in range(8):
                piece = board.board[r][c]
                # bo qua dau cham EMPTY
                if piece == EMPTY:
                    continue
                value = piece_values[piece.upper()]
                if piece.isupper():
                    score += value
                else:
                    score -= value
        return score
    # hàm minimax
    def minimax(self, board, depth, maximizing):
        # nếu độ sâu bằng 0 thì đánh giá luôn
        if depth==0:
            return self.evaluate(board)
        # nếu lớn nhất đúng thì
        if maximizing:
            # tạo ra một số vô cùng nhỏ
            max_eval = -float('inf')
            # lấy toàn bộ nước đi
            moves = board.generate_all_pseudo_moves(WHITE)
            for move in moves:
                # thực hiện di chuyển các nước đi đã liệt kê
                board.make_move(move)
                eval = self.minimax(board,depth-1,False)
                # sau khi đi xong thì hoàn lại các bước đi
                board.undo_move()
                max_eval = max(max_eval,eval)
            return max_eval
        # ngược lại
        else:
            # tạo ra một sô siêu lớn
            min_eval = float('inf')
            # lấy toàn bộ nước đi bên đen
            moves = board.generate_all_pseudo_moves(BLACK)
            for move in moves:
                board.make_move(move)
                eval = self.minimax(board,depth-1,True)
                min_eval = min(min_eval,eval)
            return min_eval
    # hàm tìm nước đi tốt nhất
    def find_best_move(self,board,color):
        # nước đi tốt nhất
        best_move = None
        # bên trắng
        if color == WHITE:
            # một số cực nhỏ
            best_value = -float('inf')
            # lấy toàn bộ nước đi
            moves = board.generate_all_pseudo_moves(WHITE)
            for move in moves:
                board.make_move(move)
                value = self.minimax(board,self.depth-1,False)
                board.undo_move()
                if value > best_value:
                    best_value = value
                    best_move = move
        # bên đen
        else:
            # một số rất lớn
            best_value = float('inf')
            moves = board.generate_all_pseudo_moves(BLACK)
            for move in moves:
                board.make_move(move)
                value = self.minimax(board,self.depth-1,True)
                board.undo_move()
                if value < best_value:
                    best_value = value
                    best_move = move
        return best_move
            






