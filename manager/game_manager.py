import logging
from core.board import Board
from core.minimax import Minimax
from constants import WHITE,BLACK
class GameManager:
    def __init__(self, ai_depth=4, ai_color=BLACK):
        self.board = Board()
        self.ai = Minimax(depth=ai_depth)
        self.ai_color = ai_color
        self.logger = logging.getLogger(self.__class__.__name__)
    def get_board_state(self):
        return self.board.board
    def reset(self):
        self.board = Board()
        self.logger.info("Reset game")
    def get_game_status(self, color):
        if self.board.is_checkmate(color):
            return{
                "state": "checkmate",
                "loser": "white" if color == WHITE else "black"
            }
        if self.board.is_stalemate(color):
            return {"state": "stalemate"}
        if self.board.is_in_check(color):
            return{
                "state": "check",
                "color": "white" if color == WHITE else "black"
            }
        return {"state": "ongoing"}
    def get_legal_moves_for(self, row, col):
        piece = self.board.get_piece(row, col)
        if piece == ".":
            return []
        moves = self.board.generate_legal_moves(row, col)
        return [{"row": m[2], "col": m[3]} for m in moves]
    def apply_player_move(self, move):
        try:
            fr, fc, tr, tc = move
            legal_moves = self.board.generate_legal_moves(fr, fc)
            matched = [m for m in legal_moves if m[2] == tr and m[3] == tc]
            if not matched:
                return False
            self.board.make_move(matched[0])
            return True
        except Exception as e:
            self.logger.error(f"Invalid move {move}: {e}")
            return False
    def compute_ai_move(self):
        if self.board.turn != self.ai_color:
            return None
        move = self.ai.find_best_move(self.board, self.ai_color)
        if move:
            self.board.make_move(move)
            self.logger.info(f"AI move: {move}")
        return move

