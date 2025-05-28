from datetime import datetime
import logging
from typing import List, Optional
from pydantic import field_validator

from app.models import Installment
from app.schemas import BaseSchema, OutSchema, StrNotEmpty
from app.schemas.creditor_schemas import CreditorOutSchema
from app.schemas.payer_schemas import PayerOutSchema


lgr = logging.getLogger(__name__)

class AgreementInSchema(BaseSchema):
    number: StrNotEmpty = None
    payer: int
    creditor: int


class AgreementPatchInSchema(BaseSchema):
    number: StrNotEmpty = None
    payer: Optional[int] = None
    creditor: Optional[int] = None

    @field_validator('payer', mode='before')
    @classmethod
    def extract_payer_id(cls, v):
        if isinstance(v, dict) and 'id' in v:
            return v['id']
        return v

    @field_validator('creditor', mode='before')
    @classmethod
    def extract_creditor_id(cls, v):
        if isinstance(v, dict) and 'id' in v:
            return v['id']
        return v


class AgreementOutSchema(OutSchema):
    number: str
    payer: PayerOutSchema
    creditor: CreditorOutSchema
    created_at: datetime
    updated_at: datetime


class AgreementHomeInSchema(BaseSchema):
    payer_id: Optional[int] = None


class AgreementHomeOutSchema(BaseSchema):
    payer: PayerOutSchema
    number: str
    creditor: CreditorOutSchema
    installments: List[Installment]
