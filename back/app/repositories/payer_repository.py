
from app.models import Payer
from app.repositories import BaseRepository


class PayerRepository(BaseRepository[Payer]):
    model = Payer
