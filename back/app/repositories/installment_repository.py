
from app.models import Installment
from app.repositories import BaseRepository


class InstallmentRepository(BaseRepository[Installment]):
    model = Installment
