# nơi này sẽ chạy mọi thứ
from board import Board
if __name__ == "__main__":
    game = Board()
    game.print_board()
    # đi thử
    game.make_move((6,4,4,4))
    game.print_board()


