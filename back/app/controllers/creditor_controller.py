import logging
from typing import Tuple

from django.core.paginator import Paginator, Page
import faker

from app.controllers import BaseController
from app.models import Creditor
from app.repositories.creditor_repository import CreditorRepository
from app.schemas import ListSchema
from app.schemas.creditor_schemas import CreditorInSchema

lgr =  logging.getLogger(__name__)

fake = faker.Faker()

class CreditorController(BaseController[CreditorRepository, Creditor]):
    REPOSITORY = CreditorRepository
    MODEL = Creditor

    @classmethod
    def create(cls, creditor_schema: CreditorInSchema) -> Creditor:
        """
        Cria um novo credor.

        Parâmetros:
            - creditor_schema: Schema do credor a ser criado.

        Retorna:
            - Creditor: Pagador criado.
        """
        creditor_data = creditor_schema.model_dump(exclude_none=True)
        
        return cls.REPOSITORY.create(creditor_data)

    @classmethod
    def filter(cls, filters: ListSchema) -> Tuple[Page, Paginator]:
        """
        Lista credores com base nos filtros fornecidos.

        Parâmetros:
            - filters: Filtros de paginação e pesquisa.

        Retorna:
            - List[Creditor]: Lista de credores.
        """
        creditors = cls.REPOSITORY.filter(filters.model_dump())
        lgr.debug(filters.page_size)
        paginator = Paginator(creditors, filters.page_size)
        page_number = filters.page

        creditors: Page = paginator.get_page(page_number)
        return creditors, paginator

