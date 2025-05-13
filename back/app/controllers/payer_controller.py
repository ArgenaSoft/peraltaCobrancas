import logging
from typing import Tuple

from django.core.paginator import Paginator, Page
import faker

from app.controllers import BaseController
from app.controllers.user_controller import UserController
from app.exceptions import HttpFriendlyException
from app.models import Payer, User
from app.repositories.payer_repository import PayerRepository
from app.repositories.user_repository import UserRepository
from app.schemas import ListSchema
from app.schemas.payer_schemas import PayerInSchema
from app.schemas.user_schemas import UserInSchema

lgr =  logging.getLogger(__name__)

fake = faker.Faker()

class PayerController(BaseController[PayerRepository, Payer]):
    REPOSITORY = PayerRepository
    MODEL = Payer

    @classmethod
    def create(cls, payer_schema: PayerInSchema) -> Payer:
        """
        Cria um novo pagador.

        Parâmetros:
            - payer_schema: Schema do pagador a ser criado.

        Retorna:
            - Payer: Pagador criado.
        """
        if UserRepository.exists(cpf=payer_schema.cpf):
            raise HttpFriendlyException(400, "Payer with this cpf already exists.")

        uc_schema: UserInSchema = UserInSchema(
            cpf=payer_schema.cpf,
            is_active=True
        )

        user: User = UserController.create(uc_schema)
        payer_data = payer_schema.model_dump(exclude_none=True)
        payer_data['user'] = user
        
        return cls.REPOSITORY.create(payer_data)

    @classmethod
    def filter(cls, filters: ListSchema) -> Tuple[Page, Paginator]:
        """
        Lista pagadores com base nos filtros fornecidos.

        Parâmetros:
            - filters: Filtros de paginação e pesquisa.

        Retorna:
            - List[Payer]: Lista de pagadores.
        """
        payers = cls.REPOSITORY.filter(filters.model_dump())
        lgr.debug(filters.page_size)
        paginator = Paginator(payers, filters.page_size)
        page_number = filters.page

        payers: Page = paginator.get_page(page_number)
        return payers, paginator

