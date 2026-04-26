from persistence.models import User
from persistence.repository.baserepository import BaseRepository

class UserRepository(BaseRepository):

    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, username, email, password_hash):
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        self.add(user)
        self.commit()
        self.refresh(user)
        return user