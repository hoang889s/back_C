# core/utils/fen.py

from core.constants import WHITE, BLACK, EMPTY
from core.board import Board
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1"
def get_start_fen() -> str:
    """Trả về FEN đầu game (không phải 'startpos')"""
    return START_FEN
def normalize_fen(fen: str) -> str:
    # handle special keyword
    if fen == "startpos":
        return START_FEN
    
    parts = fen.split()
    # thiếu turn → thêm mặc định
    if len(parts) == 1:
        return fen + " w - - 0 1"
    # thiếu field → bổ sung cho đủ 6 phần
    if len(parts) < 6:
        parts += ["-"] * (6 - len(parts))
        return " ".join(parts)
    return fen

def fen_to_board(fen: str) -> Board:
    board = Board()

    fen = normalize_fen(fen)
    parts = fen.split()

    rows = parts[0].split("/")

    new_board = []

    for row in rows:
        current_row = []
        for char in row:
            if char.isdigit():
                current_row.extend([EMPTY] * int(char))
            else:
                current_row.append(char)
        new_board.append(current_row)

    board.board = new_board

    # turn
    board.turn = WHITE if parts[1] == "w" else BLACK

    return board


def board_to_fen(board: Board) -> str:
    fen_rows = []

    for row in board.board:
        empty_count = 0
        fen_row = ""

        for cell in row:
            if cell == EMPTY:
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += cell

        if empty_count > 0:
            fen_row += str(empty_count)

        fen_rows.append(fen_row)

    fen_board = "/".join(fen_rows)

    turn = "w" if board.turn == WHITE else "b"

    return f"{fen_board} {turn} - - 0 1"