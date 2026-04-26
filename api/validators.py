from core.constants import WHITE, BLACK, EMPTY
class MoveValidator:
    @staticmethod
    def validate_position(r, c):
        # kiểm tra vị trí có nằm trong bàn cờ
        return 0 <= r < 8 and 0 <= c < 8
    @staticmethod
    def validate_source_piece(board, r, c, player_color):
        # Kiểm tra quân cờ tại vị trí nguồn có hợp lệ
        piece = board.get_piece(r, c)
        if piece == EMPTY:
            return False, "No piece at source position"
        if player_color == WHITE and not piece.isupper():
            return False, "Not your piece"
        if player_color == BLACK and not piece.islower():
            return False, "Not your piece"
        return True,None
    @staticmethod
    def validate_turn(board, player_color):
        # kiểm tra đúng lượt chơi
        if board.turn != player_color:
            return False, "Not your turn"
        return True,None
    @staticmethod
    def validate_move_format(move):
        # kiểm tra move
        # (fr, fc, tr, tc) hoặc (fr, fc, tr, tc, move_type)
        if not isinstance(move, tuple):
            return False, "Move must be tuple"
        if len(move) not in (4, 5):
            return False, "Invalid move format"
        return True, None
    @staticmethod
    def validate_legal_move(board, move):
        # Kiểm tra move có hợp lệ theo luật cờ
        if len(move) == 5:
            fr, fc, tr, tc, _ = move
        else:
            fr, fc, tr, tc = move
        legal_moves = board.generate_legal_moves(fr, fc)
        if move not in legal_moves:
            return False, "Illegal move"
        return True, None
class GameValidator:
    @staticmethod
    def is_check(board, color):
        return board.is_in_check(color)
    @staticmethod
    def is_checkmate(board, color):
        return board.is_checkmate(color)
    @staticmethod
    def is_stalemate(board, color):
        return board.is_stalemate(color)
    @staticmethod
    def validate_game_not_over(board):
        if board.is_checkmate(WHITE) or board.is_checkmate(BLACK):
            return False, "Game is over (checkmate)"
        if board.is_stalemate(WHITE) or board.is_stalemate(BLACK):
            return False, "Game is over (stalemate)"
        return True, None


