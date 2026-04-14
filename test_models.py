from database import SessionLocal, init_db
from models import User, Room, RoomPlayer, Game, Move, GameMode

# init DB (tạo bảng)
init_db()

db = SessionLocal()

try:
    # ======================
    # 1. Tạo user
    # ======================
    user1 = User(username="user1", email="u1@test.com", password_hash="123")
    user2 = User(username="user2", email="u2@test.com", password_hash="123")

    db.add_all([user1, user2])
    db.commit()

    print("Created users")

    # ======================
    # 2. Tạo room
    # ======================
    room = Room(
        name="Test Room",
        code="ABC123",
        owner_id=user1.id,
        mode=GameMode.HUMAN
    )

    db.add(room)
    db.flush()  # để lấy room.id

    print("Created room")

    # ======================
    # 3. Thêm player vào room
    # ======================
    rp1 = RoomPlayer(room_id=room.id, user_id=user1.id)
    rp2 = RoomPlayer(room_id=room.id, user_id=user2.id)

    db.add_all([rp1, rp2])
    db.commit()

    print(" Added players to room")

    # ======================
    # 4. Tạo game
    # ======================
    game = Game(
        room_id=room.id,
        white_player_id=user1.id,
        black_player_id=user2.id
    )

    db.add(game)
    db.commit()

    print(" Created game")

    # ======================
    # 5. Thêm move
    # ======================
    move1 = Move(
        game_id=game.id,
        move="e2e4",
        player_id=user1.id,
        move_number=1
    )

    move2 = Move(
        game_id=game.id,
        move="e7e5",
        player_id=user2.id,
        move_number=2
    )

    db.add_all([move1, move2])
    db.commit()

    print(" Added moves")

    # ======================
    # 6. Test relationship
    # ======================
    g = db.query(Game).first()

    print("\n TEST RELATIONSHIP")
    print("Room:", g.room.name)
    print("White:", g.white_player.username)
    print("Black:", g.black_player.username)

    print("\nMoves:")
    for m in g.moves:
        print(m.move, "by", m.player.username)

finally:
    db.close()