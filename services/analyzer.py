from core.constants import WHITE,BLACK
from core.minimax import Minimax
from core.utils.fen import fen_to_board
from core.board import Board
class Analyzer:
    def __init__(self, depth: int = 4):
        self.depth = depth
        self.engine = Minimax(depth)
    def analyze(self, board, color):
        # trả về best_move evaluation score  thông tin debug
        # init incremental evaluation
        self.engine.init_score(board)
        # tìm nước đi tốt nhất
        best_move = self.engine.find_best_move(board, color)
        # lấy score hiện tại (sau khi search xong vẫn là state ban đầu)
        score = self.engine.evaluate(board)
        # trạng thái game
        is_check = board.is_in_check(color)
        is_checkmate = board.is_checkmate(color)
        is_stalemate = board.is_stalemate(color)
        return{
            "best_move": self._format_move(best_move),
            "score": score,
            "is_check": is_check,
            "is_checkmate": is_checkmate,
            "is_stalemate": is_stalemate,
            "nodes": self.engine.node_searched,
            "tt_hits": self.engine.tt_hits
        }
    def get_top_moves(self,board, color, top_n=5):
        # trả về top n nước đi tốt nhất
        self.engine.init_score(board)
        moves = board.generate_all_legal_moves(color)
        move_scores = []
        for move in moves:
            self.engine.push_move(board, move)
            score = self.engine.minimax(
                board,
                self.depth - 1,
                -float('inf'),
                float('inf'),
                color != WHITE
            )
            self.engine.pop_move(board)
            move_scores.append((move, score))
        move_scores.sort(key=lambda x: x[1], reverse=(color == WHITE))
        return [
            {
                "move": self._format_move(m),
                "score": s,
            }
            for m, s in move_scores[:top_n]
        ]
    def _format_move(self,move):
        if not move:
            return None
        fr, fc, tr, tc = move[0], move[1], move[2], move[3]
        def to_square(r, c):
            return chr(ord('a') + c) + str(8 - r)
        move_str = f"{to_square(fr, fc)}{to_square(tr, tc)}"
        if len(move) == 5:
            move_str += f"={move[4]}"
        return move_str
    def get_best_move(self, fen, color):
        board = fen_to_board(fen)

        self.engine.init_score(board)

        best_move = self.engine.find_best_move(board, color)

        if not best_move:
            return None

        return best_move

