
from app.models import LoginCode
from app.repositories import BaseRepository


class LoginCodeRepository(BaseRepository[LoginCode]):
    model = LoginCode
