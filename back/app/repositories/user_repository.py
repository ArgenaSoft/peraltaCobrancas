
from app.models import User
from app.repositories import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User