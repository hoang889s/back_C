from board import Board
from minimax import Minimax
from constants import WHITE, BLACK, EMPTY
import sys
sys.stdout.reconfigure(encoding='utf-8')
class Game:
    def __init__(self, ai_depth=3,player_color=WHITE):
        self.board = Board()
        self.ai = Minimax(depth=ai_depth)
        self.player_color = player_color
        self.ai_color = BLACK if player_color == WHITE else WHITE
        self.col_to_idx = {
            'a':0,'b':1,'c':2,'d':3,
            'e':4,'f':5,'g':6,'h':7
        }
        self.idx_to_col = {v:k for k,v in self.col_to_idx.items()}
    # hàm chuyển đổi tọa độ
    def parse_move(self,move_str):
        # đổi e2e4 → (6,4,4,4)
        #'e2e4' → (fr, fc, tr, tc) hoặc None nếu sai định dạng
        move_str = move_str.strip().lower()
        if len(move_str)<4:
            return None
        try:
            fc = self.col_to_idx.get(move_str[0])
            fr = 8 - int(move_str[1])
            tc = self.col_to_idx.get(move_str[2])
            tr = 8 - int(move_str[3])
        except (ValueError,IndexError):
            return None
        if None in (fc,tc):
            return None
        if not (0<=fr<8 and 0<=fc<8 and 0<=tr<8 and 0<=tc<8):
            return None
        return (fr,fc,tr,tc)
    # hàm chuyển đổi tọa độ ngược lại
    def format_move(self,move):
        fr,fc,tr,tc = move[0],move[1],move[2],move[3]
        return f"{self.idx_to_col[fc]}{8 - fr}{self.idx_to_col[tc]}{8-tr}"
    # hàm xử lý lượt người chơi
    def get_player_move(self):
        # kiểm tra input người chơi trả về move hợp lệ
        while True:
            raw = input("nuoc di cua ban (vd e2e4 ,'quit' thoat)").strip()
            if raw.lower() == 'quit':
                print("ban thoat game")
                sys.exit()
            if raw.lower() == 'help':
                self._show_help()
                continue
            parsed = self.parse_move(raw)
            if not parsed:
                print("nhap sai roi hay nhap 'e2e4")
                continue
            fr,fc,tr,tc = parsed
            piece=self.board.get_piece(fr,fc)
            # kiểm tra mình có chọn đúng quân để đánh không
            if piece == EMPTY:
                print("o trong")
                continue
            if self.player_color == WHITE and not self.board.is_white(piece):
                print("khong phai quan cua ban")
                continue
            if self.player_color == BLACK and not self.board.is_black(piece):
                print("khong phai quan cua ban")
                continue
            # lấy nước đi hợp lệ
            legal_moves = self.board.generate_legal_moves(fr,fc)
            candidates  = [m for m in legal_moves if m[2]==tr and m[3]==tc]
            if not candidates:
                print("nuoc di khong hop le")
                self._suggest_moves(fr,fc)
                continue
            # xử lý phong quân
            if len(candidates)>1:
                return self._handle_promotion(candidates)
            return candidates[0]
    # hàm phong quân cho người chơi
    def _handle_promotion(self,candidates):
        # xử lý giúp người chơi chọn được quân cần phong
        print("phong quan chon Q (hau) K(vua) R(xe) B(tuong) N(ma)")
        # neu không chọn mặc định là quân hậu
        choice = input("lua chon [mac dinh Q]: ").strip().upper()
        if choice not in ('Q','R','B','N'):
            choice = 'Q'
        matched = next(
            (m for m in candidates if len(m) ==5 and m[4] == choice),candidates[0]
        )
        return matched
    # hàm gợi ý nước đi
    def _suggest_moves(self,fr,fc):
        # gợi ý các nước đi hợp tại fr fc
        legal = self.board.generate_legal_moves(fr,fc)
        if legal:
            suggestions = [self.format_move(m) for m in legal[:5]]
            print(f"Gợi ý: {', '.join(suggestions)}")
        else:
            print("khong co nuoc di hop le")
    # hàm hướng dẫn
    def _show_help(self):
        print("\n huong dan:")
        print("  - nhap nuoc di dang 'e2e4' (o xuat phat + o dich)")
        print("  - 'quit' : thoat ")
        print("  - 'help' : hien huong dan nay\n")
    # hàm lượt đánh của ai
    def do_ai_move(self):
        print("kim lien dang suy nghi...")
        ai_move = self.ai.find_best_move(self.board,self.ai_color)
        if ai_move is None:
            return False
        self.board.make_move(ai_move)
        print(f"kim lien da di {self.format_move(ai_move)}")
        return True
    # hàm kiểm tra ván cờ đã kết thúc chưa
    def check_game_over(self,color):
        if self.board.is_checkmate(color):
            self.board.print_board()
            if color == self.player_color:
                print("ban da thua")
            else:
                print("ban da thang")
            return True
        if self.board.is_stalemate(color):
            self.board.print_board()
            print("hoa co")
            return True
        # cảnh báo chiếu
        if self.board.is_in_check(color):
            if color == self.player_color:
                print("Vua cua ban dang bi chieu")
            else:
                print("kim lien dang bi chieu")
        return False
    # vòng lặp chạy game
    def run(self):
        print("="*40)
        print("dau co")
        print(f"  ban = {'trang' if self.player_color == WHITE else 'den'}"
              f"  |  kim lien = {'den' if self.ai_color == BLACK else 'trang'}")
        print("go 'help' de xem huong dan")
        print("="*40)
        while True:
            self.board.print_board()
            current = self.board.turn
            # kiểm tra chiếu hết trước mỗi lượt
            if self.check_game_over(current):
                break
            # lượt người chơi
            if current == self.player_color:
                move = self.get_player_move()
                self.board.make_move(move)
                print(f"ban da di{self.format_move(move)}")
                continue
            else:
                if not self.do_ai_move():
                    print("kim lien khong co nuoc di hop le")
                    break







