
from app.models import LoginCode
from app.repositories import BaseRepository


class LoginCodeRepository(BaseRepository[LoginCode]):
    """
    Repositório para a entidade LoginCode.
    
    Atributos:
        - model: Modelo associado ao repositório.
    """
    model = LoginCode
