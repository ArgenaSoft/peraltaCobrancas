
from app.models import Creditor
from app.repositories import BaseRepository


class CreditorRepository(BaseRepository[Creditor]):
    model = Creditor
