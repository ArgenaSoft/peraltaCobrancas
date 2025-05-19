import logging

from app.controllers import BaseController
from app.controllers.creditor_controller import CreditorController
from app.controllers.payer_controller import PayerController
from app.models import Agreement
from app.repositories.agreement_repository import AgreementRepository
from app.schemas.agreement_schemas import AgreementInSchema, AgreementPatchInSchema

lgr =  logging.getLogger(__name__)


class AgreementController(BaseController[AgreementRepository, Agreement]):
    REPOSITORY = AgreementRepository
    MODEL = Agreement

    @classmethod
    def create(cls, schema: AgreementInSchema) -> Agreement:
        """
        Cria um novo acordo.

        Parâmetros:
            - agreement_schema: Schema do acordo a ser criado.

        Retorna:
            - Agreement: Acordo criado.
        """
        data = schema.model_dump()
        data['payer'] = PayerController.get(id=schema.payer)
        data['creditor'] = CreditorController.get(id=schema.creditor)
        
        return cls.REPOSITORY.create(data)


    @classmethod
    def update(cls, id, schema: AgreementPatchInSchema) -> Agreement:
        instance = cls.REPOSITORY.get(pk=id)
        data = schema.model_dump()
        data['payer'] = PayerController.get(id=schema.payer)
        data['creditor'] = CreditorController.get(id=schema.creditor)
        return cls.REPOSITORY.update(instance, **data)
