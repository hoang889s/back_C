# nơi này sẽ chạy mọi thứ
from board import Board
from constants import WHITE, BLACK, EMPTY
from minimax import Minimax
import sys 
from game import Game
sys.stdout.reconfigure(encoding='utf-8')
# nhap thanh cho quan trang
if __name__ == "__main__":
    # Có thể thay đổi: ai_depth=4 mạnh hơn, player_color=BLACK để đi quân đen
    game = Game(ai_depth=4, player_color=WHITE)
    game.run()




