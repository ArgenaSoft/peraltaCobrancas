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
from app.schemas import PayerSchema, UserSchema

lgr =  logging.getLogger(__name__)

fake = faker.Faker()

class PayerController(BaseController[PayerRepository, PayerSchema, Payer]):
    REPOSITORY = PayerRepository
    SCHEMA = PayerSchema
    MODEL = Payer

    @classmethod
    def create(cls, payer_schema: PayerSchema.In) -> Payer:
        """
        Cria um novo pagador.

        Parâmetros:
            - payer_schema: Schema do pagador a ser criado.

        Retorna:
            - Payer: Pagador criado.
        """
        if UserRepository.exists(payer_schema.cpf):
            raise HttpFriendlyException(400, "Payer with this cpf already exists.")

        uc_schema: UserSchema.In = UserSchema.In(
            cpf=payer_schema.cpf,
            is_active=True
        )

        user: User = UserController.create(uc_schema)
        payer_data = payer_schema.model_dump(exclude_none=True)
        payer_data['user_id'] = user.pk
        
        return cls.REPOSITORY.create(payer_data)

    @classmethod
    def filter(cls, filters: PayerSchema.List) -> Tuple[Page, Paginator]:
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

