from app.controllers import BaseController
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas import UserSchema


class UserController(BaseController[UserRepository, UserSchema, User]):
    REPOSITORY = UserRepository
    SCHEMA = UserSchema
    MODEL = User

    @classmethod
    def create(cls, user_schema: UserSchema.In) -> User:
        """
        Cria um novo pagador.

        Parâmetros:
            - user_schema: Schema do usuário a ser criado.

        Retorna:
            - User: Usuário criado.
        """
        user = UserRepository.create(user_schema.model_dump(exclude_none=True))
        return user