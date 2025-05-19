import logging

from app.controllers import BaseController
from app.controllers.user_controller import UserController
from app.exceptions import HttpFriendlyException
from app.models import Payer, User
from app.repositories.payer_repository import PayerRepository
from app.repositories.user_repository import UserRepository
from app.schemas.payer_schemas import PayerInSchema
from app.schemas.user_schemas import UserInSchema

lgr =  logging.getLogger(__name__)

class PayerController(BaseController[PayerRepository, Payer]):
    REPOSITORY = PayerRepository
    MODEL = Payer

    @classmethod
    def create(cls, schema: PayerInSchema) -> Payer:
        """
        Cria um novo pagador.

        Parâmetros:
            - schema: Schema do pagador a ser criado.

        Retorna:
            - Payer: Pagador criado.
        """
        if UserRepository.exists(cpf=schema.cpf):
            raise HttpFriendlyException(400, "Um usuário com esse cpf já existe!")

        uc_schema: UserInSchema = UserInSchema(
            cpf=schema.cpf,
            is_active=True
        )

        user: User = UserController.create(uc_schema)
        data = schema.model_dump()
        data['user'] = user
        
        return cls.REPOSITORY.create(data)

