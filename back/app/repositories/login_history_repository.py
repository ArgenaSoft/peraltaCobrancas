
from app.models import LoginHistory
from app.repositories import BaseRepository


class LoginHistoryRepository(BaseRepository[LoginHistory]):
    model = LoginHistory
