
from app.models import Boleto
from app.repositories import BaseRepository


class BoletoRepository(BaseRepository[Boleto]):
    """
    Repositório para a entidade Boleto.
    
    Atributos:
        - model: Modelo associado ao repositório.
    """
    model = Boleto
