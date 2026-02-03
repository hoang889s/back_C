# nơi này sẽ chạy mọi thứ
from board import Board
from constants import WHITE, BLACK, EMPTY
# nhap thanh cho quan trang
def test_white_castling_kingside():
    print(" nhâp thanh quân trang")
    # khoi tao
    game = Board()
    # tao một bàn cờ đi
    game.board = [
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['R', '.', '.', '.', 'K', '.', '.', 'R'],
    ]
    game.white_king_moved = False
    game.white_rook_moved['a'] = False
    game.white_rook_moved['h'] = False
    moves = game.generate_king_moves(7, 4)
    print("nhap thanh quan trang")
    assert (7, 4, 7, 6, 'castle') in moves
    print("ok")
    print(moves)
# nhap thanh canh hau
def test_white_castling_queenside():
    print("nhap thanh canh hau")
    game = Board()
    game.board = [
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['R', '.', '.', '.', 'K', '.', '.', 'R'],
    ]
    game.white_king_moved = False
    game.white_rook_moved['a'] = False
    game.white_rook_moved['h'] = False
    moves = game.generate_king_moves(7, 4)
    print("nhap thanh canh hau")
    assert (7, 4, 7, 2, 'castle') in moves
    print("ok")
    print(moves)
# trương hợp không hợp lệ
def test_white_castling_faild_king_move():
    print("trương hop khi nhap thanh that bai vi da di quan")
    game = Board()
    game.board[7][4] = 'K'
    game.white_king_moved = True
    moves = game.generate_king_moves(7, 4)
    print("nuoc di cua quan vua",moves)
    assert all(len(m) != 5 for m in moves)
    print("ok")
# trương hợp bị chiếu
def test_white_castling_faild_in_check():
    print(" nhap thanh khi quan vua bi chiếu")
    game = Board()
    # tạo bàn cờ có quân xe bị chiếu
    game.board = [
        ['.', '.', '.', '.', 'r', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['R', '.', '.', '.', 'K', '.', '.', 'R'],
    ]
    moves = game.generate_king_moves(7, 4)
    print(" cac nuoc di cua quan vua khi bi chiếu")
    assert (7, 4, 7, 6, 'castle') not in moves
    print("test thanh cong")
if __name__ == "__main__":
    test_white_castling_kingside()
    test_white_castling_queenside()
    test_white_castling_faild_king_move()
    test_white_castling_faild_in_check()




