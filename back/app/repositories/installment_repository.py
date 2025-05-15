
from app.models import Installment
from app.repositories import BaseRepository


class InstallmentRepository(BaseRepository[Installment]):
    """
    Repositório para a entidade Installment.
    
    Atributos:
        - model: Modelo associado ao repositório.
    """
    model = Installment
