
from app.models import Creditor
from app.repositories import BaseRepository


class CreditorRepository(BaseRepository[Creditor]):
    """
    Repositório para a entidade Creditor.
    
    Atributos:
        - model: Modelo associado ao repositório.
    """
    model = Creditor
