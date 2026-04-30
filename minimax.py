from core.constants import WHITE, BLACK, EMPTY
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
# giá trị quân cờ
PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330,
    'R': 500, 'Q': 900, 'K': 20000
}
# MVV-LVA bảng ưu tiên giá trị nạn nhân cao -> điểm cao giá trị tấn công cao -> điểm cao
# vd Tốt ăn hậu -> ngon hậu ăn tốt -> không ngon
MVV_LVA = {
    ('P','P'):15,('P','N'):25,('P','B'):25,('P','R'):35,('P','Q'):45,
    ('N','P'):14,('N','N'):24,('N','B'):24,('N','R'):34,('N','Q'):44,
    ('B','P'):13,('B','N'):23,('B','B'):23,('B','R'):33,('B','Q'):43,
    ('R','P'):12,('R','N'):22,('R','B'):22,('R','R'):32,('R','Q'):42,
    ('Q','P'):11,('Q','N'):21,('Q','B'):21,('Q','R'):31,('Q','Q'):41,
}
PST = {
    'P':PAWN_TABLE,
    'N':KNIGHT_TABLE,
    'B':BISHOP_TABLE,
    'R':ROOK_TABLE,
    'Q':QUEEN_TABLE,
    'K':KING_TABLE_MIDDLE
}
# Hàm tính PST bonus cho một quân (dùng cho incremental eval)
def _piece_score(piece:str,r:int,c:int)->int:
    p_type = piece.upper()
    value = PIECE_VALUES.get(p_type,0)
    table = PST.get(p_type)
    if piece.isupper():
        bonus = table[r][c] if table else 0
        return value + bonus
    else:
        bonus = table[7-r][c] if table else 0
        return -(value + bonus)
class Minimax:
    def __init__(self,depth):
        # khoi tao
        self.depth = depth
        # giảm bớt các chuỗi nước đi lặp lại lưu(zobrist_hash)
        self.transposition_table:dict = {}
        # giới hạn kích thước bảng TT
        self.TT_MAX_SIZE= 1_000_000
        # hỗ trợ việc cắt tỉa apla-beta mạnh hơn
        self.killer_moves = [[None, None] for _ in range(64)]
        # tăng khả năng search sâu
        self.history_table: dict ={}
        # biến đếm node đã duyệt
        self.node_searched = 0
        # Tìm thấy vị trí trong transposition table
        self.tt_hits =  0
        # score hiện tại của bàn cờ (tính từ đầu, cập nhật tăng dần)
        self._inc_score:int = 0
        # stack lưu lại delta mỗi khi make_move để undo_move khôi phục
        self._score_stack: list = []
    # Tính điểm đầy đủ từ bàn cờ hiện tại (gọi 1 lần trước khi search)
    def init_score(self,board)->None:
        score = 0
        for r in range(8):
            for c in range(8):
                p = board.board[r][c]
                if p != EMPTY:
                    score += _piece_score(p, r, c)
        self._inc_score = score
        self._score_stack.clear()
    # Cập nhật _inc_score theo move VÀ gọi board.make_move.
    # Phải gọi thay cho board.make_move() trực tiếp khi dùng incremental eval.
    def push_move(self,board,move:tuple)->None:
        # tách thông tin vị trí các quân cờ
        fr,fc,tr,tc = move[0], move[1], move[2], move[3]
        move_type = move[4] if len(move) == 5 else None
        # lấy quân cờ hiện tại
        piece = board.board[fr][fc]
        # lấy quân cờ bị ăn
        captured = board.board[tr][tc]
        delta = 0
        # Bỏ quên đang đứng khỏi ô cũ
        delta -= _piece_score(piece, fr, fc)
        # Bỏ quân nếu bị ăn (nếu có)
        if captured != EMPTY:
            delta -= _piece_score(captured, tr, tc)
        # Đặt quân lên ô mới
        if move_type and move_type.startswith("promotion"):
            promo_char = move_type.split("_")[1]
            landing = promo_char.upper() if piece.isupper() else promo_char.lower()
        else:
            landing = piece
        delta += _piece_score(landing, tr, tc)
        # Nhập thành câp nhật cả xe
        if move_type == "castle":
            # quân trắng
            if piece == 'K':
                # cánh vua
                if tc == 6:
                    delta -= _piece_score('R', 7, 7)
                    delta += _piece_score('R', 7, 5)
                # cánh hậu
                else:
                    delta -= _piece_score('R', 7, 0)
                    delta += _piece_score('R', 7, 3)
            elif piece == 'k':
                if tc == 6:
                    delta -= _piece_score('r', 0, 7)
                    delta += _piece_score('r', 0, 5)
                else:
                    delta -= _piece_score('r', 0, 0)
                    delta += _piece_score('r', 0, 3)
        self._score_stack.append(self._inc_score)
        self._inc_score += delta
        board.make_move(move)
    # Hoàn tác move và khôi phục _inc_score
    def pop_move(self, board) -> None:
        board.undo_move()
        self._inc_score = self._score_stack.pop()
    # ham gia ban co
    # ham nay danh gia diem so cac quan co
    def evaluate(self, board) -> int:
       return self._inc_score
    # hàm xét nước mạnh trước
    def _move_score(self, move, board, depth:int, tt_move=None) -> int:
        fr, fc, tr, tc = move[0], move[1], move[2], move[3]
        target = board.board[tr][tc]
        attacker = board.board[fr][fc]
        # Hash move từ TT – ưu tiên cao nhất
        if move == tt_move:
            return 30_000
        # Ăn quân ưu tiên ăn quân cao nhất vd Tốt ăn Hậu → 10000 + 45 = 10045
        if target != EMPTY:
            return 10_000 + MVV_LVA.get((attacker.upper(),target.upper()),0)
        # killer move
        if move == self.killer_moves[depth][0]: return 9_000
        if move == self.killer_moves[depth][1]:return 8_000
        # history heuristic
        return self.history_table.get((move[0], move[1], move[2], move[3]),0)
    # 
    def _order_moves(self, moves, board, depth: int, tt_move = None):
        # sắp xếp
        return sorted(moves,key=lambda m: self._move_score(m, board, depth, tt_move),reverse=True)
    # hoạt động với nguyên lý khi có killer mới thì killer lên ví trí số một và killer cũ lên vị xuống số 2 
    # giảm node sớm
    def _update_killer(self,move,depth:int)->None:
        if move !=self.killer_moves[depth][0]:
            self.killer_moves[depth][1] =self.killer_moves[depth][0]
            self.killer_moves[depth][0] = move
    # khi sắp xếp move sẽ ưu tiên những move có vị trí cao 
    def _update_history(self,move,depth: int)-> None:
        #key = (move[0],move[1])
        key = (move[0], move[1], move[2], move[3])
        self.history_table[key]=self.history_table.get(key,0)+depth*depth
    # khi depth = 0 thì không dừng tìm kiếm mà tiếp tục tìm quân mới và đường đi mới
    # tăng khả năng đánh giá
    def quiescence(self,board,alpha,beta,maximizing,q_depth:int=4):
        # đánh giá điểm bình thường
        stand_pat = self.evaluate(board)
        # nếu maximizing đúng 
        if maximizing:
            # cắt nhánh
            if stand_pat >= beta:
                return beta
            alpha = max(alpha,stand_pat)
            # đặt ra giới hạn để tránh search vô hạn
            if q_depth == 0:
                return alpha
            #captures = [m for m in board.generate_all_pseudo_moves(WHITE)
            #           if board.board[m[1][0]][m[1][1]]!=EMPTY]
            captures = [m for m in board.generate_all_pseudo_moves(WHITE)
                        if board.board[m[2]][m[3]] != EMPTY]
            for move in self._order_moves(captures,board,0):
                self.push_move(board, move)
                # board.make_move(move)
                # đệ quy gọi lại
                score = self.quiescence(board,alpha,beta,False,q_depth-1)
                #board.undo_move()
                self.pop_move(board)
                if score >= beta:
                    return beta
                alpha = max(alpha,score)
            return alpha
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta,stand_pat)
            if q_depth == 0:
                return beta
            #captures = [m for m in board.generate_all_pseudo_moves(BLACK)
                        #if board.board[m[1][0]][m[1][1]] != EMPTY]
            captures = [m for m in board.generate_all_pseudo_moves(BLACK)
                        if board.board[m[2]][m[3]] != EMPTY]

            for move in self._order_moves(captures,board,0):
                #board.make_move(move)
                self.push_move(board, move)
                score = self.quiescence(board,alpha,beta,True,q_depth-1)
                #board.undo_move()
                self.pop_move(board)
                if score <= alpha: return alpha
                beta = min(beta, score)
            return beta
    # hàm minimax kết hợp alpha,beta
    def minimax(self,board,depth:int,alpha,beta, maximizing)-> int:
        # mỗi lần search tăng giá trị của node lên 1
        self.node_searched +=1
        # lưu alpha gốc
        alpha_orig = alpha
        # lấy hash của board
        board_hash = board.get_hash() if hasattr(board,'get_hash') else None
        # best move được lưu trong TT
        tt_move = None
        # kiểm tra xem có trong bảng hash không
        if board_hash and board_hash in self.transposition_table:
            # lấy dữ liệu
            tt_depth, tt_flag, tt_score, tt_best = self.transposition_table[board_hash]
            # khi đủ độ sâu
            if tt_depth >= depth:
                self.tt_hits += 1
                # cập nhật các giá trị cắt tỉa alpha beta
                if tt_flag == 'EXACT':
                    return tt_score
                if tt_flag == 'LOWER':
                    alpha = max(alpha,tt_score)
                if tt_flag == 'UPPER':
                    beta = min(beta,tt_score)
                if alpha >= beta:
                    return tt_score
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
            return self.quiescence(board,alpha,beta,maximizing)
        # lấy nước đi hợp lệ
        all_moves = self._order_moves(board.generate_all_pseudo_moves(current_color),board,depth,tt_move)
        # Nếu ngay cả khi mình không đi mà vẫn không thua, thì mình đang quá mạnh.
        # tối ưu khả search cho thuật toán
        if (depth>=3 and hasattr(board,'make_null_move')and not board.is_in_check(current_color) and all_moves):
            board.make_null_move()
            null_score = self.minimax(board,depth-3,alpha,beta,not maximizing)
            board.undo_null_move()
            if maximizing and null_score >= beta:
                return beta
            if not maximizing and null_score<=alpha:
                return alpha 
        best_score = -float('inf') if maximizing else float('inf')
        best_move_local = None 
        for i,move in enumerate(all_moves):
            #board.make_move(move)
            fr, fc, tr, tc = move[0], move[1], move[2], move[3]
            is_capture = board.board[tr][tc] != EMPTY 
           # board.make_move(move)           
            #skip = False
            if i>=4 and depth>=3 and not is_capture and move not in self.killer_moves[depth]:
                self.push_move(board,move)
                lmr_score =  self.minimax(board,depth-2,alpha,beta,not maximizing)
                self.pop_move(board)
                if(maximizing and lmr_score <= alpha) or (not maximizing and lmr_score >=beta):
                    #board.undo_move()
                    # undo xong mới continue
                    continue
            #if not skip:
                #eval_score = self.minimax(board,depth-1,alpha,beta,not maximizing)
            #board.undo_move()
            #if skip:
                #continue
            self.push_move(board,move)
            eval_score = self.minimax(board, depth - 1, alpha, beta, not maximizing)
            #board.undo_move()
            self.pop_move(board)
            # nếu maximizing đúng tìm điểm lớn nhất
            if maximizing:
                # cập nhật best_score
                if eval_score >best_score:
                    best_score = eval_score
                if eval_score > alpha:
                    alpha = eval_score
                # cắt nhánh
                if alpha >= beta:
                # Nếu là non-capture → cập nhật heuristic
                    if not is_capture:
                        self._update_killer(move,depth)
                        self._update_history(move,depth)
                    break
            else:
                if eval_score < best_score: 
                    best_score = eval_score
                if eval_score < beta:      
                    beta = eval_score
                if beta <= alpha:
                    if not is_capture:
                        self._update_killer(move, depth)
                        self._update_history(move, depth)
                    break
        # Lưu vào Transposition Table
        #if board_hash:
        #    flag = ('UPPER' if best_score<= alpha_orig else 'LOWER' if best_score>=beta else'EXACT')
        #    if len(self.transposition_table)<self.TT_MAX_SIZE:
        #        self.transposition_table[board_hash] = (depth,flag,best_score)
        #return best_score
        if board_hash and len(self.transposition_table) < self.TT_MAX_SIZE:
            if   best_score <= alpha_orig: flag = 'UPPER'
            elif best_score >= beta:       flag = 'LOWER'
            else:                          flag = 'EXACT'
            self.transposition_table[board_hash] = (depth, flag, best_score, best_move_local)
        
        return best_score


    # hàm tìm nước đi tốt nhất
    def find_best_move(self,board,color):
        # reset thông số
        # số node đã search
        self.node_searched =0
        # số lần trung Transposition Table
        self.tt_hits = 0
        # killer move cho lần tìm mới
        self.killer_moves = [[None,None] for _ in range(64)]
        # xác định là mã hay min
        maximizing = (color==WHITE)
        best_move  = None
        # duyệt depth với khả năng tăng dần
        for current_depth in range(1,self.depth+1):
            # khởi tạo alpha beta
            alpha = -float('inf')
            beta = float('inf')
            # lưu best move cho depth hiện tại
            depth_best_move = None
            depth_best_value = -float('inf') if maximizing else float('inf')
            # lấy tất cả các nước đi
            moves = board.generate_all_legal_moves(color)
            # ưu tiên những thứ tốt nhất lên đầu tiên
            if best_move and best_move in moves:
                moves.remove(best_move)
                moves.insert(0,best_move)
            # duyệt move ở root
            for move in moves:
                #board.make_move(move)
                self.push_move(board,move)
                value = self.minimax(board,current_depth-1,alpha,beta,not maximizing)
                # hoàn tác nước đi
                #board.undo_move()
                self.pop_move(board)
                # cắt tỉa
                if maximizing:
                    if value > depth_best_value:
                        depth_best_value,depth_best_move = value,move
                    alpha = max(alpha,value)
                else:
                    if value < depth_best_value:
                        depth_best_value,depth_best_move = value,move
                    beta = min(beta,value)
            if depth_best_move:
                best_move = depth_best_move
        return best_move

       
         

   





