
from app.models import Agreement
from app.repositories import BaseRepository


class AgreementRepository(BaseRepository[Agreement]):
    model = Agreement
