from app.controllers import BaseController
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserInSchema


class UserController(BaseController[UserRepository, User]):
    REPOSITORY = UserRepository
    MODEL = User

    @classmethod
    def create(cls, schema: UserInSchema) -> User:
        """
        Cria um novo pagador.

        Parâmetros:
            - schema: Schema do usuário a ser criado.

        Retorna:
            - User: Usuário criado.
        """
        data = schema.model_dump(exclude_none=True)
        
        return cls.REPOSITORY.create(data)
