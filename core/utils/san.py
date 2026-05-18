from core.constants import WHITE, WHITE_PIECES, BLACK_PIECES,PIECE_NAMES
def to_square(row, col):
    return chr(ord('a') + col) + str(8 - row)
def move_to_san(board, move, color):
    fr, fc, tr, tc = move[:4]
    special = move[4] if len(move) == 5 else None
    if special == "castle":
        if tc > fc:
            return "O-O"
        else:        # Queenside
            return "O-O-O"

    
    piece = board.board[fr][fc]
    captured = board.board[tr][tc]
    is_capture = captured != "."

     # --- En passant detection ---
    if piece.upper() == "P" and fc != tc and captured == ".":
        is_capture = True  # en passant

    if piece.upper() == "P":
        san = ""
        if is_capture:
            san = chr(ord('a') + fc) + "x"
        san += to_square(tr, tc)
        # Promotion
        if special and special.upper() in ['Q', 'R', 'B', 'N']:
            san += "=" + special.upper()
        # Check/Checkmate suffix added later
        return _add_check_suffix(board, move, san, color)
    

    # --- Piece moves ---
    piece_letter = PIECE_NAMES.get(piece, "")
    san = piece_letter
    
    # Disambiguation: check if another piece of same type can reach same square
    own_pieces = WHITE_PIECES if color == WHITE else BLACK_PIECES
    legal_moves = board.generate_all_legal_moves(color)

    ambiguous_moves = [
        m for m in legal_moves
        if (m[2], m[3]) == (tr, tc)           # same destination
        and board.board[m[0]][m[1]] == piece   # same piece type
        and (m[0], m[1]) != (fr, fc)           # different origin
    ]

    if ambiguous_moves:
        same_file = any(m[1] == fc for m in ambiguous_moves)
        same_rank = any(m[0] == fr for m in ambiguous_moves)
        
        if not same_file:
            san += chr(ord('a') + fc)       # add file
        elif not same_rank:
            san += str(8 - fr)              # add rank
        else:
            san += chr(ord('a') + fc) + str(8 - fr)  # add both

    if is_capture:
        san += "x"

    san += to_square(tr, tc)

    return _add_check_suffix(board, move, san, color)

def _add_check_suffix(board, move, san, color):
    """Add + or # suffix after making the move on a clone."""
    import copy
    test_board = copy.deepcopy(board)
    test_board.make_move(move)
    
    opponent = "black" if color == WHITE else "white"
    
    if test_board.is_checkmate(opponent):
        return san + "#"
    elif test_board.is_in_check(opponent):
        return san + "+"
    return san


            