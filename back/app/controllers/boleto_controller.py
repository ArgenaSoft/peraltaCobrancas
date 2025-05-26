import logging

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from ninja import UploadedFile

from app.controllers import BaseController
from app.controllers.agreement_controller import AgreementController
from app.controllers.installment_controller import InstallmentController
from app.models import Agreement, Boleto, Creditor, Installment
from app.repositories.boleto_repository import BoletoRepository
from app.schemas.boleto_schemas import BoletoInSchema, BoletoPatchInSchema

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
        installment: Installment = InstallmentController.get(id=schema.installment)
        agreement: Agreement = installment.agreement
        creditor: Creditor = agreement.creditor

        path = cls._save_boleto_pdf(schema.pdf, creditor.slug_name, agreement.slug_name, installment.slug_name)

        data = schema.model_dump()
        data['pdf'] = path
        data['installment'] = installment

        return cls.REPOSITORY.create(data)


    @classmethod
    def update(cls, id, schema: BoletoPatchInSchema) -> Boleto:
        instance = cls.REPOSITORY.get(pk=id)
        data = schema.model_dump()
        
        if schema.installment:
            data['installment'] = InstallmentController.get(id=schema.installment)

        if schema.pdf:
            instance.pdf.delete(save=False)
            installment: Installment = instance.installment
            agreement: Agreement = installment.agreement
            creditor: Creditor = agreement.creditor

            path = cls._save_boleto_pdf(schema.pdf, creditor.slug_name, agreement.slug_name, installment.slug_name)
            data['pdf'] = path

        updated: Boleto = cls.REPOSITORY.update(instance, **data)
        AgreementController.check_agreement_status(updated.installment.agreement)

    @classmethod
    def _save_boleto_pdf(cls, pdf: UploadedFile, creditor_name: str, agreement_name: str, installment_name: str) -> str:
        """
        Salva o arquivo PDF do boleto no sistema de arquivos.

        Parâmetros:
            - pdf: O arquivo PDF a ser salvo.
            - creditor_name: Nome do credor.
            - agreement_name: Nome do acordo.
            - installment_name: Nome da parcela.

        Retorna:
            - str: O caminho do arquivo salvo.
        """
        path = f"boletos/{creditor_name}/{agreement_name}_{installment_name}.pdf"
        path = default_storage.save(path, ContentFile(pdf.file.read()))
        return path