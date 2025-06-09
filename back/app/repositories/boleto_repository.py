
from app.models import Boleto
from app.repositories import BaseRepository


class BoletoRepository(BaseRepository[Boleto]):
    model = Boleto
