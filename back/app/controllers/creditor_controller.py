import logging

from app.controllers import BaseController
from app.models import Creditor
from app.repositories.creditor_repository import CreditorRepository
from app.schemas.creditor_schemas import CreditorInSchema

lgr =  logging.getLogger(__name__)


class CreditorController(BaseController[CreditorRepository, Creditor]):
    REPOSITORY = CreditorRepository
    MODEL = Creditor

    @classmethod
    def create(cls, schema: CreditorInSchema) -> Creditor:
        """
        Cria um novo credor.

        Parâmetros:
            - schema: Schema do credor a ser criado.

        Retorna:
            - Creditor: Pagador criado.
        """
        data = schema.model_dump()
        
        return cls.REPOSITORY.create(data)


