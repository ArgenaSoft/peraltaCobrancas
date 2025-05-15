import logging

from app.controllers import BaseController
from app.controllers.agreement_controller import AgreementController
from app.models import Agreement, Installment
from app.repositories.agreement_repository import AgreementRepository
from app.repositories.installment_repository import InstallmentRepository
from app.schemas.installment_schemas import InstallmentInSchema

lgr =  logging.getLogger(__name__)

class InstallmentController(BaseController[InstallmentRepository, Installment]):
    REPOSITORY = InstallmentRepository
    MODEL = Installment

    @classmethod
    def create(cls, schema: InstallmentInSchema) -> Installment:
        agreement: Agreement = AgreementRepository.get(id=schema.agreement) 
        data = schema.model_dump(exclude_none=True)
        data['agreement'] = agreement

        return cls.REPOSITORY.create(data)


    @classmethod
    def update(cls, id, schema: InstallmentInSchema) -> Agreement:
        instance = cls.REPOSITORY.get(pk=id)
        data = schema.model_dump()
        data['agreement'] = AgreementController.get(id=schema.agreement)

        return cls.REPOSITORY.update(instance, **data)
