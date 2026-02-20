from constants import WHITE, BLACK, EMPTY
# bảng đánh giá thưởng phạt của quân tốt, mã , xe ,vua,hậu
PAWN_TABLE = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [ 5,  5, 10, 25, 25, 10,  5,  5],
    [ 0,  0,  0, 20, 20,  0,  0,  0],
    [ 5, -5,-10,  0,  0,-10, -5,  5],
    [ 5, 10, 10,-20,-20, 10, 10,  5],
    [ 0,  0,  0,  0,  0,  0,  0,  0]
]
KNIGHT_TABLE = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]
BISHOP_TABLE = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]
ROOK_TABLE = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [ 0,  0,  0,  5,  5,  0,  0,  0]
]
QUEEN_TABLE = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [ -5,  0,  5,  5,  5,  5,  0, -5],
    [  0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]
KING_TABLE_MIDDLE = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [ 20, 20,  0,  0,  0,  0, 20, 20],
    [ 20, 30, 10,  0,  0, 10, 30, 20]

]
PST = {
    'P':PAWN_TABLE,
    'N':KNIGHT_TABLE,
    'B':BISHOP_TABLE,
    'R':ROOK_TABLE,
    'Q':QUEEN_TABLE,
    'K':KING_TABLE_MIDDLE
}
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
                # lấy quân cờ hiện tại
                piece = board.board[r][c]
                # nếu là dấu chấm bỏ qua
                if piece == EMPTY:
                    continue
                # chuyển toàn bộ giá trị sang chữ hoa
                p_type = piece.upper()
                # tạo giá trị vừa lấy được
                value = piece_values[p_type]
                # gán bảng đánh giá
                table = PST.get(p_type,None)
                # quân trắng
                if piece.isupper():
                    pos_bonus = table[r][c] if table else 0
                    score += value + pos_bonus
                else:
                    pos_bonus = table[7-r][c] if table else 0
                    score -= (value+pos_bonus) 
        return score
    # hàm minimax kết hợp alpha,beta
    def minimax(self,board,depth,alpha,beta, maximizing):
        current_color = WHITE if maximizing else BLACK
        # kết thúc bàn cờ
        if board.is_checkmate(current_color):
            # bị chiếu hết (thua)
            return -99999 if maximizing else 99999
        # nếu không bị chiếu hết
        if board.is_stalemate(current_color):
            return 0;# hòa
        # nếu độ sâu bằng 0 thì đánh giá
        if depth == 0:
            return self.evaluate(board)
        # lấy nước đi hợp lệ
        all_moves = board.generate_all_pseudo_moves(current_color)
        # nếu maximizing đúng
        if maximizing:
            # một số cực nhỏ
            max_eval = -float('inf')
            for move in all_moves:
                board.make_move(move)
                # gọi đệ quy cho trường hợp max
                eval_score = self.minimax(board,depth-1,alpha,beta,False)
                # hoàn tác nước đi
                board.undo_move()
                max_eval = max(max_eval,eval_score)
                alpha = max(alpha,eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in all_moves:
                board.make_move(move)
                eval_score = self.minimax(board,depth-1,alpha,beta,True)
                board.undo_move()
                min_eval = min(min_eval,eval_score)
                beta = min(beta,eval_score)
                if beta <= alpha:
                    break
            return min_eval
# hàm tìm nước đi
def find_best_move(self,board,color):
    # tạo best_move rỗng 
    best_move = None
    # bên quân trắng
    if color == WHITE:
        # giá trị nhỏ nhất
        best_value = -float('inf')
        # một số rất nhỏ và một số rất lớn
        alpha = -float('inf')
        beta = float('inf')
        # lấy toàn bộ nước đi hợp lệ
        moves = board.generate_all_legal_moves(WHITE)
        for move in moves:
            value = self.minimax(board,self.depth-1,alpha,beta,False)
            # hoàn tác nước đi
            board.undo_move()
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha,value)
    else:
        best_value = float('inf')
        moves = board.generate_all_legal_moves(BLACK)
        for move in moves:
            value = self.minimax(boar,self.depth-1,alpha,beta,True)
            board.undo_move()
            if value < best_value:
                best_value = value
                best_move = move
            beta = min(beta,value)
    return best_move

         

   





