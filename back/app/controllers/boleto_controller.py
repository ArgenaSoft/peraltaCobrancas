import logging

from app.controllers import BaseController
from app.controllers.installment_controller import InstallmentController
from app.models import Boleto
from app.repositories.boleto_repository import BoletoRepository
from app.schemas.boleto_schemas import BoletoInSchema

lgr =  logging.getLogger(__name__)


class BoletoController(BaseController[BoletoRepository, Boleto]):
    REPOSITORY = BoletoRepository
    MODEL = Boleto

    @classmethod
    def create(cls, schema: BoletoInSchema) -> Boleto:
        """
        Cria um novo boleto.

        Parâmetros:
            - boleto_schema: Schema do acordo a ser criado.

        Retorna:
            - Boleto: Acordo criado.
        """
        data = schema.model_dump(exclude_none=True)
        data['installment'] = InstallmentController.get(id=schema.boleto)
        
        return cls.REPOSITORY.create(data)


    @classmethod
    def update(cls, id, schema: BoletoInSchema) -> Boleto:
        instance = cls.REPOSITORY.get(pk=id)
        data = schema.model_dump()
        data['installment'] = InstallmentController.get(id=schema.boleto)
        
        return cls.REPOSITORY.update(instance, **data)
