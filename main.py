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
        game.make_move(knight_move[1])
    game.print_board()



