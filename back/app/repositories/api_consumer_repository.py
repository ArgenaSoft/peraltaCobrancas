
from app.models import ApiConsumer
from app.repositories import BaseRepository


class ApiConsumerRepository(BaseRepository[ApiConsumer]):
    """
    Repositório para a entidade ApiConsumer.
    
    Atributos:
        - model: Modelo associado ao repositório.
    """
    model = ApiConsumer
