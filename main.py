# nơi này sẽ chạy mọi thứ
from board import Board
if __name__ == "__main__":
    game = Board()
    game.print_board()
    # đi thử

    # quân tôt đi thử
    pawn_move = game.generate_pawn_moves(6,4)
    print("cac nuoc di hop le cua e2:")
    print(pawn_move)
    if pawn_move:
        game.make_move(pawn_move[1])
    game.print_board()
    knight_move = game.generate_knight_moves(7,6)
    print(knight_move)
    if knight_move:
        game.make_move(knight_move[0])
    game.print_board()
    bishop_move = game.generate_bishop_moves(7,5)
    print(bishop_move)
    if bishop_move:
        game.make_move(bishop_move[4])
    game.print_board()
    pawn_move = game.generate_pawn_moves(6, 7)
    print(pawn_move)
    if pawn_move:
        game.make_move(pawn_move[1])
    game.print_board()
    rook_move = game.generate_rook_moves(7, 7)
    print(rook_move)
    if rook_move:
        game.make_move(rook_move[1])
    game.print_board()
    queen_move = game.generate_queen_moves(7, 3)
    print(queen_move)
    if queen_move:
        game.make_move(queen_move[0])
    game.print_board()
    king_move = game.generate_king_moves(7, 4)
    print(king_move)
    if king_move:
        game.make_move(king_move[0])
    game.print_board()


