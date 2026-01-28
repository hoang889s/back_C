# nơi này sẽ chạy mọi thứ
from board import Board
from constants import WHITE, BLACK, EMPTY
if __name__ == "__main__":
    game = Board()
    # reset bàn cờ về rỗng
    # tương tự tạo ra hai vòng lặp
    game.board = [[EMPTY for _ in range(8)] for _ in range(8)]
    # đặt vua vào nếu không is_in_check kiểm tra không hợp thì sẽ lỗi
    game.board[7][4] = 'K'
    game.board[0][4] = '.'
    # đặt một quân tốt để phong quân
    game.board[1][4] = 'P'
    # in bàn cờ
    game.print_board()
    # bắt đầu phong quân
    pawn_moves = game.generate_pawn_moves(1, 4)
    print(" cac nươc di cua quan tot e7 :")
    print(pawn_moves)
    # test make move
    move = pawn_moves[0]
    game.make_move(move)
    game.print_board()
    # test undo move
    game.undo_move()
    game.print_board()
    # test legal move
    legal = game.generate_legal_moves(1, 4)
    print("Legal promotion moves:")
    print(legal)



