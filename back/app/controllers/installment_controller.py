from datetime import date
import logging

from app.controllers import BaseController
from app.models import Agreement, Boleto, Installment
from app.repositories.agreement_repository import AgreementRepository
from app.repositories.installment_repository import InstallmentRepository
from app.schemas.installment_schemas import InstallmentInSchema, InstallmentPatchInSchema

lgr =  logging.getLogger(__name__)

class InstallmentController(BaseController[InstallmentRepository, Installment]):
    REPOSITORY = InstallmentRepository
    MODEL = Installment

    @classmethod
    def create(cls, schema: InstallmentInSchema) -> Installment:
        agreement: Agreement = AgreementRepository.get(id=schema.agreement) 
        data = schema.model_dump()
        data['agreement'] = agreement

        return cls.REPOSITORY.create(data)

    @classmethod
    def update(cls, id, schema: InstallmentPatchInSchema) -> Installment:
        instance = cls.REPOSITORY.get(pk=id)
        data = schema.model_dump()
        data['agreement'] = AgreementRepository.get(id=schema.agreement)

        return cls.REPOSITORY.update(instance, **data)

    @classmethod
    def remove_overdue_installments(cls):
        # Calculo a data de hoje
        # Pego todas as parcelas com 'data de vencimento menor que hoje
        # E que não foram pagas' e as removo
        today = date.today()
        overdue_installments = cls.REPOSITORY.filter(due_date__lt=today, boleto__status=Boleto.Status.PENDING)
        lgr.debug(f"Encontradas {len(overdue_installments)} parcelas vencidas para remoção.")
        for installment in overdue_installments:
            lgr.debug(f'Removendo parcela vencida: {installment.agreement.number} -> Parcela {installment.id} - Vencimento: {installment.due_date}')
            cls.REPOSITORY.delete(installment)
