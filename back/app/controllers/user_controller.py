from app.controllers import BaseController
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserInSchema


class UserController(BaseController[UserRepository, User]):
    REPOSITORY = UserRepository
    MODEL = User

    @classmethod
    def create(cls, user_schema: UserInSchema) -> User:
        """
        Cria um novo pagador.

        Parâmetros:
            - user_schema: Schema do usuário a ser criado.

        Retorna:
            - User: Usuário criado.
        """
        user = UserRepository.create(user_schema.model_dump(exclude_none=True))
        return user