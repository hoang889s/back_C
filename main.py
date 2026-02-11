# nơi này sẽ chạy mọi thứ
from board import Board
from constants import WHITE, BLACK, EMPTY
from minimax import Minimax
import sys 
sys.stdout.reconfigure(encoding='utf-8')
# nhap thanh cho quan trang
if __name__ == "__main__":
    board = Board()
    ai = Minimax(depth=3)
    best_move = ai.find_best_move(board,WHITE)
    print("AI",best_move)
    board.make_move(best_move)
    board.print_board()
    




