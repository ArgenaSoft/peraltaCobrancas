
from datetime import date
from typing import List, Optional
from app.schemas import BaseSchema


class ProcessSpreadsheetResponse(BaseSchema):
    job_id: str


class BoletoSchema(BaseSchema):
    path: str
    readonly: bool = False


class InstallmentSchema(BaseSchema):
    agreement_num: str
    number: int
    due_date: date
    boleto: Optional[BoletoSchema] = None

    readonly: bool = False
    deleted: bool


class AgreementSchema(BaseSchema):
    number: str
    payer_cpf_cnpj: str
    creditor_name: str
    installments: List[InstallmentSchema]

    readonly: bool = False
    deleted: bool


class UserSchema(BaseSchema):
    cpf_cnpj: str
    readonly: bool = False


class PayerSchema(BaseSchema):
    name: str
    user: UserSchema
    phone: str
    agreements: List[AgreementSchema]

    readonly: bool = False
    deleted: bool


class CreditorSchema(BaseSchema):
    name: str
    reissue_margin: int
    readonly: bool = False
    deleted: bool


class SaveSpreadsheetSchema(BaseSchema):
    payers: List[PayerSchema]
    creditors: List[CreditorSchema]