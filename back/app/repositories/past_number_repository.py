
from app.models import PastNumber
from app.repositories import BaseRepository


class PastNumberRepository(BaseRepository[PastNumber]):
    model = PastNumber
