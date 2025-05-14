from datetime import datetime
import logging
from pydantic import field_validator

from app.schemas import BaseSchema, StrNotEmpty
from app.schemas.creditor_schemas import CreditorOutSchema
from app.schemas.payer_schemas import PayerOutSchema


lgr = logging.getLogger(__name__)

class AgreementInSchema(BaseSchema):
    number: StrNotEmpty = None
    payer: int
    creditor: int


class AgreementPatchInSchema(BaseSchema):
    number: StrNotEmpty = None
    payer: int
    creditor: int

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


class AgreementOutSchema(BaseSchema):
    number: str
    payer: PayerOutSchema
    creditor: CreditorOutSchema
    created_at: datetime
    updated_at: datetime
