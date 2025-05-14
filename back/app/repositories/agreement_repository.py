
from app.models import Agreement
from app.repositories import BaseRepository


class AgreementRepository(BaseRepository[Agreement]):
    """
    Repositório para a entidade Agreement.
    
    Atributos:
        - model: Modelo associado ao repositório.
    """
    model = Agreement
