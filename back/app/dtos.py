from datetime import date
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, PrivateAttr, computed_field

from app.models import Creditor, Installment, User


lgr = logging.getLogger(__name__)


class BoletoDTO(BaseModel):
    path: str
    readonly: bool = False

    @classmethod
    def from_database(cls, boleto) -> "BoletoDTO":
        return cls(
            path=boleto.pdf.path,
            readonly=False,
        )


class InstallmentDTO(BaseModel):
    agreement_num: str
    number: int
    due_date: date
    boleto: Optional[BoletoDTO] = None

    readonly: bool = False

    @classmethod
    def from_database(cls, installment: Installment) -> "InstallmentDTO":
        if hasattr(installment, 'boleto'):
            boleto_dto = BoletoDTO.from_database(installment.boleto)
        else:
            boleto_dto = None

        return cls(
            agreement_num=installment.agreement.number,
            number=int(installment.number),
            due_date=installment.due_date,
            boleto=boleto_dto,
            readonly=True,
        )


class AgreementDTO(BaseModel):
    number: str
    payer_cpf_cnpj: str
    creditor_name: str
    installments: List[InstallmentDTO]

    readonly: bool = False

    @classmethod
    def from_database(cls, agreement) -> "AgreementDTO":
        return cls(
            number=agreement.number,
            payer_cpf_cnpj=agreement.payer.user.cpf_cnpj,
            creditor_name=agreement.creditor.name,
            installments=[],
            readonly=True,
        )


class UserDTO(BaseModel):
    cpf_cnpj: str
    readonly: bool = False

    @classmethod
    def from_database(cls, user: User) -> "UserDTO":
        return cls(
            cpf_cnpj=user.cpf_cnpj,
            readonly=True,
        )


class PayerDTO(BaseModel):
    name: str
    user: UserDTO
    phone: str
    agreements: List[AgreementDTO]

    readonly: bool = False

    @classmethod
    def from_database(cls, payer) -> "PayerDTO":
        return cls(
            name=payer.name,
            user=UserDTO.from_database(payer.user),
            phone=payer.phone,
            agreements=[],
            readonly=True,
        )



class CreditorDTO(BaseModel):
    name: str
    reissue_margin: int
    readonly: bool = False

    @classmethod
    def from_database(cls, creditor: Creditor) -> "CreditorDTO":
        return cls(
            name=creditor.name,
            reissue_margin=creditor.reissue_margin,
            readonly=True,
        )


class SpreadsheetDTO(BaseModel):
    payers: List[PayerDTO]
    _creditor_cache: Dict[str, CreditorDTO] = PrivateAttr(default_factory=dict)
    errors: List[str]
    warnings: List[str]

    @computed_field
    @property
    def creditors(self) -> List[CreditorDTO]:
        return list(self._creditor_cache.values())

    def add_node(self, payer: PayerDTO, agreement: Optional[AgreementDTO] = None, installment: Optional[InstallmentDTO] = None):
        # Adiciona o pagador se não existir
        existing_payer = next((p for p in self.payers if p.user.cpf_cnpj == payer.user.cpf_cnpj), None)
        if not existing_payer:
            self.payers.append(payer)
            existing_payer = payer

        if agreement:
            # Adiciona o acordo se não existir
            existing_agreement = next((a for a in existing_payer.agreements if a.number == agreement.number), None)
            if not existing_agreement:
                existing_payer.agreements.append(agreement)
                existing_agreement = agreement

            if installment:
                # Adiciona a parcela se não existir
                existing_installment = next((i for i in existing_agreement.installments if i.number == installment.number), None)
                if not existing_installment:
                    existing_agreement.installments.append(installment)
    
    def add_creditor(self, creditor: CreditorDTO):
        lgr.debug("====================")
        lgr.debug(self._creditor_cache)
        lgr.debug("====================")
        if creditor.name not in self._creditor_cache:
            self._creditor_cache[creditor.name] = creditor
            return
        
        lgr.debug(f"Credor {creditor.name} já existe nos resultados, não adicionando novamente.")

    @classmethod
    def from_json(cls, data: Dict) -> 'SpreadsheetDTO':
        # Reconstrói o DTO a partir dos dados JSON
        dto = cls(
            payers=[PayerDTO(**payer) for payer in data.get('payers', [])],
            errors=data.get('errors', []),
            warnings=data.get('warnings', []),
        )

        # Reconstrói o cache de credores
        for creditor in data.get('creditors', []):
            creditor_dto = CreditorDTO(**creditor)
            dto._creditor_cache[creditor_dto.name] = creditor_dto

        return dto
