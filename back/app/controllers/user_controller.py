import re
from typing import Union

from app.controllers import BaseController
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import AdminInSchema, UserInSchema


class UserController(BaseController[UserRepository, User]):
    REPOSITORY = UserRepository
    MODEL = User

    @classmethod
    def create(cls, schema: Union[UserInSchema, AdminInSchema]) -> User:
        """
        Cria um novo pagador.

        Parâmetros:
            - schema: Schema do usuário a ser criado.

        Retorna:
            - User: Usuário criado.
        """
        data = schema.model_dump()
        data['cpf_cnpj'] = re.sub(r"\D", "", data['cpf_cnpj'])
        
        return cls.REPOSITORY.create(data)

