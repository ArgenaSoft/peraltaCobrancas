
from app.models import Payer
from app.repositories import BaseRepository


class PayerRepository(BaseRepository[Payer]):
    """
    Repositório para a entidade Payer.
    
    Atributos:
        - model: Modelo associado ao repositório.
    """
    model = Payer