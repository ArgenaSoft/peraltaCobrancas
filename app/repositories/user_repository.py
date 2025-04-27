
from app.models import User
from app.repositories import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repositório para a entidade User.
    
    Atributos:
        - model: Modelo associado ao repositório.
    """
    model = User