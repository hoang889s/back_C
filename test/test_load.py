"""
Test script để kiểm tra backend
Chạy: python test_backend.py
"""

from persistence.database import SessionLocal
from services.game_manager import GameManager

def test_game_manager():
    db = SessionLocal()
    gm = GameManager(db)
    
    print("=" * 50)
    print("Testing GameManager.load_game()")
    print("=" * 50)
    
    try:
        # Test load game with ID 1
        game = gm.load_game(1)
        
        if game:
            print("✅ Game loaded successfully!")
            print(f"Game ID: {game.get('id')}")
            print(f"Status: {game.get('status')}")
            print(f"Board type: {type(game.get('board'))}")
            print(f"Board length: {len(game.get('board', []))}")
            print(f"Keys in game: {list(game.keys())}")
        else:
            print("❌ Game NOT found! game = None")
            print("Check if game with ID 1 exists in database")
            
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_game_manager()