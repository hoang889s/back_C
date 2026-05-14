from core.board import Board
from core.constants import WHITE, BLACK,DIFFICULTY_DEPTH_MAP
from persistence.repository.gamerepository import GameRepository
from persistence.repository.roomplayerrepository import RoomPlayerRepository
from persistence.repository.roomrepository import RoomRepository
from persistence.repository.userepository import UserRepository
from persistence.models import Move, Turn, GameResult
from core.utils.fen import board_to_fen, fen_to_board
from datetime import datetime
from services.analyzer import Analyzer 
from core.minimax import Minimax

class GameManager:
    def __init__(self, db):
        self.db = db
        self.games = {}  # Cache cho AI analysis
        self.game_repo = GameRepository(db)
        self.room_repo = RoomRepository(db)
        self.room_player_repo = RoomPlayerRepository(db)
        self.user_repo = UserRepository(db)
        self.DIFFICULTY_DEPTH_MAP = {
            'easy': 2,
            'medium': 4,
            'hard': 6,
            'expert': 8
        }

    def create_game(self, room_code,ai_difficulty=None):
        """Tạo game mới"""
        room = self.room_repo.get_by_code(room_code)
        if not room:
            raise Exception("Room not found")

        
        players = self.room_player_repo.get_players(room.id)
        if len(players) < 1:
            raise Exception("Not enough players")

        
        white_id = players[0].user_id
        black_id = players[1].user_id if len(players) > 1 else None


        game = self.game_repo.create_game(
            room_id=room.id,
            white_id=white_id,
            black_id=black_id,
            ai_difficulty=ai_difficulty
        )

        board = Board()
        self.games[game.id] = {
            "board": board,
            "turn": WHITE,
            "room_id": room.id
        }
        return game

    def load_game(self, game_id, use_cache=False):
        """
        Load game từ database
        
        Args:
            game_id: ID của game
            use_cache: Nếu True, dùng cached version (cho AI analysis)
                      Nếu False, load fresh từ DB (mặc định, an toàn hơn)
        
        Returns:
            dict: {"board": Board, "turn": color, "room_id": ..., "players": [...]}
        """
        # Dùng cache chỉ nếu yêu cầu (cho AI analysis)
        if use_cache and game_id in self.games:
            print(f"[GameManager] Using cached game {game_id}")
            return self.games[game_id]
        
        print(f"[GameManager] Loading game {game_id} from database...")
        
        # Load fresh game model từ database
        game_model = self.game_repo.get_game(game_id)
        if not game_model:
            raise Exception("Game not found")
        
        print(f"[GameManager] Game model loaded: FEN={game_model.fen}, turn={game_model.turn.value}")
        
        # Load board từ FEN (không replay moves - hiệu quả hơn)
        board = fen_to_board(game_model.fen)
        
        game = {
            "board": board,
            "turn": board.turn,
            "room_id": game_model.room_id,
            "white_id": game_model.white_player_id,
            "black_id": game_model.black_player_id,
        }
        
        # Load players từ room
        room_players = self.room_player_repo.get_players(game_model.room_id)
        game["players"] = [p.user_id for p in room_players]
        
        print(f"[GameManager] Game loaded: {len(game['players'])} players, board.turn={board.turn}")
        
        # Chỉ cache nếu yêu cầu
        if use_cache:
            self.games[game_id] = game
        
        return game

    def make_move(self, game_id, move_str, player_id, promotion):
        """
        Di chuyển quân cờ
        
        Args:
            game_id: ID của game
            move_str: Move string (chess notation, e.g., 'e2e4')
            player_id: ID của player đang đi
            promotion: Promotion piece (Q, R, B, N) hoặc None
        
        Returns:
            dict: {
                "move": move_str,
                "promotion": promotion,
                "turn": next_turn,
                "is_check": bool,
                "is_checkmate": bool,
                "is_stalemate": bool,
                "game_status": str,
                "winner": int or None
            }
        """
        print(f"\n[GameManager] ========== MAKE_MOVE START ==========")
        print(f"[GameManager] game_id={game_id}, move_str={move_str}, player_id={player_id}, promotion={promotion}")
        
        #  Load fresh game model từ database (không dùng cache)
        game_model = self.game_repo.get_game(game_id)
        if not game_model:
            print(f"[GameManager] ❌ Game {game_id} not found")
            raise Exception("Game not found")
        
        print(f"[GameManager] Game: is_ai={getattr(game_model, 'is_ai', False)}")
        print(f"[GameManager] Players: white={game_model.white_player_id}, black={game_model.black_player_id}")
        print(f"[GameManager] Current turn: {game_model.turn.value}")
        print(f"[GameManager] Current FEN: {game_model.fen}")
        
        #  Load board từ FEN (fresh state)
        board = fen_to_board(game_model.fen)
        print(f"[GameManager] Board loaded from FEN, board.turn={board.turn}")
        is_ai_game = getattr(game_model, 'is_ai', False)
        if is_ai_game:
            print(f"[GameManager] 🤖 AI Mode detected")
            if player_id == game_model.white_player_id:
                if game_model.black_player_id is not None:
                    if game_model.black_player_id != player_id:
                        print(f"[GameManager] ✅ Player {player_id} is white (human)")
                else:
                    print(f"[GameManager] ⚠️ AI (black) chưa được assign")
            elif player_id == game_model.black_player_id:
                if game_model.white_player_id is not None:
                    if game_model.white_player_id != player_id:
                        print(f"[GameManager] ✅ Player {player_id} is black (human)")
                else:
                    print(f"[GameManager] ⚠️ AI (white) chưa được assign")
            else:
                print(f"[GameManager] ❌ Player {player_id} not in this game!")
                raise Exception(f"Player {player_id} is not in this game")
            

        
        #  Validate player turn
        if game_model.turn == Turn.WHITE:
            expected_player = game_model.white_player_id
            expected_color = "WHITE"
        else:
            expected_player = game_model.black_player_id
            expected_color = "BLACK"
        
        print(f"[GameManager] Expected player: {expected_player} ({expected_color})")
        
        if player_id != expected_player:
            print(f"[GameManager] ❌ Player {player_id} is not {expected_color} (expected {expected_player})")
            raise Exception(f"Not your turn. Expected {expected_color} player (ID: {expected_player})")
        
        print(f"[GameManager] ✅ Player turn validated")
        
        #  Parse move (convert chess notation to tuple)
        try:
            move = self._parse_move(move_str, promotion=promotion)
            print(f"[GameManager] Parsed move: {move}")
        except Exception as e:
            print(f"[GameManager] ❌ Parse error: {e}")
            raise
        
        #  Generate all legal moves and validate
        print(f"[GameManager] Generating legal moves for color {board.turn}...")
        legal_moves = board.generate_all_legal_moves(board.turn)
        print(f"[GameManager] Legal moves count: {len(legal_moves)}")
        if len(legal_moves) <= 20:
            print(f"[GameManager] All legal moves: {legal_moves}")
        else:
            print(f"[GameManager] First 20 legal moves: {legal_moves[:20]}")
        
        if move not in legal_moves:
            print(f"[GameManager] ❌ Move {move} NOT in legal moves!")
            print(f"[GameManager]    Requested: {move}")
            print(f"[GameManager]    Available: {legal_moves}")
            raise Exception(f"Invalid move: {move_str}")
        
        print(f"[GameManager] ✅ Move is legal")
        
        #  Make the move on board
        print(f"[GameManager] Making move on board...")
        board.make_move(move)
        print(f"[GameManager] ✅ Move made, new turn: {board.turn}")
        
        #  Update game model in database
        print(f"[GameManager] Updating game state in database...")
        result = self._update_game_state(game_model, board,is_ai_game = is_ai_game)
        print(f"[GameManager] ✅ Game state updated")
        
        #  Clear cache (game state changed)
        if game_id in self.games:
            print(f"[GameManager] Clearing cache for game {game_id}")
            del self.games[game_id]
        
        print(f"[GameManager] ========== MAKE_MOVE END ==========\n")
        
        #  Return result (đúng format)
        return {
            "move": move_str,
            "promotion": promotion,
            "turn": board.turn,
            "is_check": result["is_check"],
            "is_checkmate": result["is_checkmate"],
            "is_stalemate": result["is_stalemate"],
            "game_status": result["game_status"],
            "winner": result["winner"],
        }

    def _update_game_state(self, game_model, board,is_ai_game=False):
        """
        Update game state in database after a move
        
        Returns:
            dict: {
                "is_check": bool,
                "is_checkmate": bool,
                "is_stalemate": bool,
                "game_status": str (enum value),
                "winner": int or None
            }
        """
        #  Convert board to FEN
        new_fen = board_to_fen(board)
        new_turn = Turn.BLACK if board.turn == BLACK else Turn.WHITE
        
        print(f"[GameManager] Updating game state:")
        print(f"  - Old FEN: {game_model.fen}")
        print(f"  - New FEN: {new_fen}")
        print(f"  - Old turn: {game_model.turn.value}")
        print(f"  - New turn: {new_turn.value}")
        
        #  Check for check/checkmate/stalemate
        is_check = board.is_in_check(board.turn)
        is_checkmate = board.is_checkmate(board.turn)
        is_stalemate = board.is_stalemate(board.turn)
        
        print(f"  - Check: {is_check}, Checkmate: {is_checkmate}, Stalemate: {is_stalemate}")
        
        #  Initialize result
        result = {
            "is_check": is_check,
            "is_checkmate": is_checkmate,
            "is_stalemate": is_stalemate,
            "game_status": GameResult.ONGOING.value,
            "winner": None,
        }
        
        #  Update FEN and turn
        game_model.fen = new_fen
        game_model.turn = new_turn
        
        #  Handle checkmate
        if is_checkmate:
            # Người vừa di chuyển là người thắng
            if new_turn == Turn.WHITE:
                winner = game_model.black_player_id
                game_model.status = GameResult.WIN if is_ai_game else GameResult.ONGOING
                print(f"[GameManager] CHECKMATE: Black player {winner} wins!")
            else:
                winner = game_model.white_player_id
                game_model.status = GameResult.WIN if is_ai_game else GameResult.ONGOING
                print(f"[GameManager] CHECKMATE: White player {winner} wins!")
            
            game_model.end_reason = "checkmate"
            game_model.ended_at = datetime.now()
            result["game_status"] = GameResult.WIN.value if is_ai_game else "checkmate"
            result["winner"] = winner
        
        #  Handle stalemate (draw)
        elif is_stalemate:
            game_model.status = GameResult.DRAW
            game_model.end_reason = "stalemate"
            game_model.ended_at = datetime.now()
            result["game_status"] = GameResult.DRAW.value
            print(f"[GameManager] STALEMATE: Draw")
        
        #  Commit to database
        self.db.add(game_model)
        self.db.flush()
        
        print(f"[GameManager] Game {game_model.id} updated in database")
        
        return result

    def _parse_move(self, move_str, promotion=None):
        """
        Convert move string (e.g., 'e2e4') to tuple
        
        Args:
            move_str: String like 'e2e4', 'e1g1' (castling)
            promotion: 'Q', 'R', 'B', 'N' (for pawn promotion)
        
        Returns:
            tuple: (from_row, from_col, to_row, to_col)
                   or (from_row, from_col, to_row, to_col, move_type)
                   where move_type is 'castle' or 'promotion_Q' etc.
        """
        def to_index(sq):
            """Convert square like 'e2' to (row, col)"""
            col = ord(sq[0]) - ord('a')  # 0-7
            row = 8 - int(sq[1])          # 0-7
            return row, col
        
        print(f"[GameManager] Parsing move: {move_str}, promotion={promotion}")
        
        # Validate format
        if not isinstance(move_str, str) or len(move_str) != 4:
            raise Exception(f"Invalid move format: {move_str}. Expected 4 characters like 'e2e4'")
        
        try:
            from_sq = move_str[:2]
            to_sq = move_str[2:4]
            
            fr = to_index(from_sq)  # (row, col)
            to = to_index(to_sq)    # (row, col)
            
            print(f"[GameManager] From: {from_sq} ({fr[0]}, {fr[1]})")
            print(f"[GameManager] To: {to_sq} ({to[0]}, {to[1]})")
            
        except (ValueError, IndexError) as e:
            raise Exception(f"Invalid move format: {move_str}. {str(e)}")
        
        #  Detect castling (king move 2 squares horizontally)
        if fr[1] == 4 and abs(to[1] - fr[1]) == 2:  # Column e = index 4
            if fr[0] in (0, 7):  # Row 0 (black) or 7 (white)
                print(f"[GameManager] Detected castling move")
                return (fr[0], fr[1], to[0], to[1], "castle")
        
        #  Handle promotion
        if promotion:
            promotion = promotion.upper()
            if promotion not in ['Q', 'R', 'B', 'N']:
                raise Exception(f"Invalid promotion piece: {promotion}. Must be Q, R, B, or N")
            # Validate destination is rank 1 or 8
            if to[0] not in (0,7):
                raise Exception(f"Promotion only allowed on rank 1 or 8, got rank {8 - to[0]}")
            print(f"[GameManager] Promotion detected: {promotion}")
            return (fr[0], fr[1], to[0], to[1], f"{promotion}")
        return (fr[0],fr[1],to[0],to[1])

    def ai_move(self, game_id, analyzer=None,difficulty=None):
        """
        AI makes a move
        
        Args:
            game_id: Game ID
            analyzer: Analyzer instance
        
        Returns:
            dict: Similar to make_move() return value
        """
        print(f"\n[GameManager] ========== AI_MOVE START ==========")
        print(f"[GameManager] game_id={game_id}")
        
        # Load fresh game model
        game_model = self.game_repo.get_game(game_id)
        if not game_model:
            raise Exception("Game not found")
        
        is_ai_game = getattr(game_model, 'is_ai', False)
        if not is_ai_game:
            print(f"[GameManager] ❌ This is not an AI game!")
            raise Exception("Not an AI game")

        ai_difficulty =difficulty or getattr(game_model, 'ai_difficulty', 'medium')
        depth = self.DIFFICULTY_DEPTH_MAP.get(ai_difficulty, 4)

        print(f"[GameManager] 🤖 AI Mode - Difficulty: {ai_difficulty} (depth={depth})")
        print(f"[GameManager] 🤖 AI Mode - Current turn: {game_model.turn.value}")
        
        print(f"[GameManager] Game: white={game_model.white_player_id}, black={game_model.black_player_id}")
        print(f"[GameManager] FEN: {game_model.fen}")
        
        # Load board from FEN
        board = fen_to_board(game_model.fen)
        
        if game_model.turn == Turn.WHITE:
            ai_player_id = game_model.white_player_id
            color = WHITE
        else:
            ai_player_id = game_model.black_player_id
            color = BLACK
        print(f"[GameManager] 🤖 AI ({color}) is thinking...")

        try:
            if analyzer is None:
                analyzer = Analyzer(depth=depth)
            else:
                analyzer.depth = depth
                analyzer.engine = Minimax(depth)
            
            best_move = analyzer.get_best_move(game_model.fen, color)
            if not best_move:
                raise Exception("AI could not find move")
            
            move_str = self._move_to_notation(best_move)

            promotion = None
            if len(best_move) == 5:
                piece = best_move[4]
                if isinstance(piece, str) and piece.upper() in ['Q', 'R', 'B', 'N']:
                    promotion = piece.upper()
                    print(f"[GameManager] 🤖 Promotion detected: {promotion}")
           

            print(f"[GameManager] 🤖 AI chose: {move_str} (promotion: {promotion})")

        except Exception as e:
            print(f"[GameManager] ❌ Analyzer error: {e}")
            # Fallback: Generate random legal move
            legal_moves = board.generate_all_legal_moves(color)
            if not legal_moves:
                print(f"[GameManager] ❌ No legal moves available!")
                raise Exception("No legal moves available")
            import random
            move = random.choice(legal_moves)
            move_str = self._move_to_notation(move)
            promotion = None
            print(f"[GameManager] 🤖 Fallback move: {move_str}")
        try:
            result = self.make_move(game_id, move_str, ai_player_id, promotion)
            print(f"[GameManager] ========== AI_MOVE END ==========\n")
            return result
        except Exception as e:
            print(f"[GameManager] ❌ AI move failed: {e}")
            raise
    
    def resign_game(self, game_id, player_id):
        """Xử lý resignation"""
        game_model = self.game_repo.get_game(game_id)
        if not game_model:
            raise Exception("Game not found")
        
        if game_model.status != GameResult.ONGOING:
            raise Exception("Game is not ongoing")
        
        if player_id == game_model.white_player_id:
            game_model.black_won = True
            winner_id = game_model.black_player_id
            loser_id = game_model.white_player_id
            print(f"[GameManager] White resigned. Black wins!")
        elif player_id == game_model.black_player_id:
            game_model.white_won = True
            winner_id = game_model.white_player_id
            loser_id = game_model.black_player_id
            print(f"[GameManager] Black resigned. White wins!")
        else:
            raise Exception("Player not in game")
        
        game_model.end_reason = "resignation"
        game_model.resigned_by = player_id
        game_model.ended_at = datetime.now()
        
        self.db.add(game_model)
        self.db.flush()
        
        return {
            "game_status": game_model.status.value,
            "winner": winner_id,
            "loser": loser_id,
            "reason": "resignation"
        }
    
    def offer_draw(self, game_id, player_id):
        """Đề nghị hòa"""
        game_model = self.game_repo.get_game(game_id)
        if not game_model:
            raise Exception("Game not found")
        
        if game_model.status != GameResult.ONGOING:
            raise Exception("Game is not ongoing")
        
        game_model.draw_offered_by = player_id
        self.db.add(game_model)
        self.db.flush()
        
        print(f"[GameManager] Player {player_id} offered draw in game {game_id}")
        
        return {"game_id": game_id, "player_id": player_id}
    
    def accept_draw(self, game_id, player_id):
        """Chấp nhận hòa"""
        game_model = self.game_repo.get_game(game_id)
        if not game_model:
            raise Exception("Game not found")
        
        if game_model.status != GameResult.ONGOING:
            raise Exception("Game is not ongoing")
        
        game_model.status = GameResult.DRAW
        game_model.end_reason = "draw_agreed"
        game_model.ended_at = datetime.now()
        
        self.db.add(game_model)
        self.db.flush()
        
        print(f"[GameManager] Game {game_id} ended in draw")
        
        return {"game_status": game_model.status.value, "reason": "draw_agreed"}
    def _move_to_notation(self, move):
        """
        Convert move tuple -> chess notation

        Example:
        (6, 4, 4, 4) -> e2e4
        (1, 4, 3, 4) -> e7e5
        """
        if not move:
            return None

        from_row, from_col, to_row, to_col = move[:4]

        def to_square(row, col):
            file_char = chr(ord('a') + col)
            rank_char = str(8 - row)
            return file_char + rank_char

        move_str = (
            to_square(from_row, from_col) +
            to_square(to_row, to_col)
        )

    # Promotion
        if len(move) == 5:
            promotion_piece = move[4]
            if isinstance(promotion_piece, str) and promotion_piece.upper() in ['Q', 'R', 'B', 'N']:
                move_str += promotion_piece.lower()

        return move_str