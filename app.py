from flask import Flask,request,jsonify
from flask_cors import CORS
from board import Board
from minimax import Minimax
from constants import WHITE,BLACK,EMPTY
# tạo server flask
app = Flask(__name__)
CORS(app)
# khởi tạo board và minimax
board = Board()
thien = Minimax(depth=4)
# cách phương thức lấy dữ liệu dọc dữ liệu
# GET lấy dữ liệu board (bàn cờ)
@app.route("/board",methods=["GET"])
def get_board():
    # trả về dạng json của bàn cờ
    return jsonify(board.board)
# POST tạo gửi dữ liệu nước di chuyển của người chơi
@app.route("/move",methods=["POST"])
def player_move():
    data = request.json
    move  = data["move"]
    board.make_move(tuple(move))
    return jsonify({"status":"ok"})
# GET gửi dữ liệu của ai khi ai thực hiện đánh nước đi
@app.route("/ai-move",methods=["GET"])
def ai_move():
    move = thien.find_best_move(board,BLACK)
    if move:
        board.make_move(move)
        return jsonify({"move":move})
    return jsonify({"move":None})
# hàm chính 
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    print(f"Server đang chạy tại: http://{host}:{port}")
    app.run(host=host,port=port,debug=True)
