import datetime
import logging
from typing import Any, Optional

from pydantic import field_validator

from app.models import Boleto
from app.schemas import BaseSchema
from app.schemas.installment_schemas import InstallmentOutSchema


lgr = logging.getLogger(__name__)

class BoletoInSchema(BaseSchema):
    pdf: Any
    installment: int
    status: Boleto.Status
    due_date: datetime.date


class BoletoPatchInSchema(BaseSchema):
    pdf: Any
    installment: Optional[int] = None
    status: Optional[Boleto.Status]
    due_date: Optional[datetime.date]

    @field_validator('installment', mode='before')
    @classmethod
    def extract_installment_id(cls, v):
        if isinstance(v, dict) and 'id' in v:
            return v['id']
        return v


class BoletoOutSchema(BaseSchema):
    pdf: Any
    installment: InstallmentOutSchema
    status: Boleto.Status
    due_date: datetime.date
