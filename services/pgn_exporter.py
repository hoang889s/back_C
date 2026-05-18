
"""
PGN (Portable Game Notation) exporter.
Generates standard PGN from a Game model and its moves.

PGN format reference: https://en.wikipedia.org/wiki/Portable_Game_Notation
"""
from datetime import datetime


class PGNExporter:
    """Generate PGN strings from Game models."""

    def export(self, game, white_name="White", black_name="Black"):
        """
        Generate full PGN string for a game.
        
        Args:
            game: Game model with .moves relationship loaded
            white_name: White player's username
            black_name: Black player's username
        
        Returns:
            str: Complete PGN string
        """
        headers = self._build_headers(game, white_name, black_name)
        movetext = self._build_movetext(game)
        return headers + "\n" + movetext + "\n"

    def _build_headers(self, game, white_name, black_name):
        """Build PGN header tags."""
        result_str = self._get_result_string(game)
        date_str = game.created_at.strftime("%Y.%m.%d") if game.created_at else "????.??.??"
        
        headers = [
            f'[Event "Online Chess Game"]',
            f'[Site "Chess Online"]',
            f'[Date "{date_str}"]',
            f'[Round "-"]',
            f'[White "{white_name}"]',
            f'[Black "{black_name}"]',
            f'[Result "{result_str}"]',
        ]
        
        if game.is_ai:
            ai_diff = getattr(game, 'ai_difficulty', 'medium')
            headers.append(f'[AILevel "{ai_diff}"]')
        
        return "\n".join(headers)

    def _build_movetext(self, game):
        """
        Build the movetext section from game moves.
        
        Uses SAN if available, falls back to coordinate notation.
        Format: 1. e4 e5 2. Nf3 Nc6 ...
        """
        moves = sorted(game.moves, key=lambda m: m.move_number)
        parts = []
        
        for move in moves:
            notation = move.san if move.san else move.move
            
            # Odd move_number = White's move, Even = Black's
            if move.move_number % 2 == 1:
                move_num = (move.move_number + 1) // 2
                parts.append(f"{move_num}. {notation}")
            else:
                parts.append(notation)
        
        # Append result
        result_str = self._get_result_string(game)
        parts.append(result_str)
        
        return " ".join(parts)

    def _get_result_string(self, game):
        """Convert game result to PGN result string."""
        if game.end_reason == "checkmate":
            if game.white_won:
                return "1-0"
            elif game.black_won:
                return "0-1"
        elif game.end_reason == "resignation":
            if game.white_won:
                return "1-0"
            elif game.black_won:
                return "0-1"
        elif game.end_reason in ("stalemate", "draw_agreed"):
            return "1/2-1/2"
        
        # Game still ongoing
        return "*"
