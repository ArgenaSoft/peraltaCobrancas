import logging
from typing import Optional

from pydantic import field_validator

from app.schemas import BaseSchema, StrNotEmpty
from app.schemas.agreement_schemas import AgreementOutSchema


lgr = logging.getLogger(__name__)

class InstallmentInSchema(BaseSchema):
    number: StrNotEmpty = None
    agreement: int


class InstallmentPatchInSchema(BaseSchema):
    number: Optional[StrNotEmpty] = None
    agreement: Optional[int] = None

    @field_validator('agreement', mode='before')
    @classmethod
    def extract_agreement_id(cls, v):
        if isinstance(v, dict) and 'id' in v:
            return v['id']
        return v


class InstallmentOutSchema(BaseSchema):
    number: str
    agreement: AgreementOutSchema
    
