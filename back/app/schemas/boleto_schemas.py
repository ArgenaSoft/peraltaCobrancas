import logging
from typing import IO, Any, Optional, Union

from ninja import UploadedFile
from pydantic import field_validator

from app.models import Boleto
from app.schemas import BaseSchema, OutSchema


lgr = logging.getLogger(__name__)

class BoletoInSchema(BaseSchema):
    # Arquivo é obrigatório, mas não faz parte do body JSON; vem via multipart.
    pdf: Optional[Union[IO[bytes], Any]] = None
    installment: int
    status: Boleto.Status


class BoletoPatchInSchema(BaseSchema):
    pdf: Optional[UploadedFile] = None
    installment: Optional[int] = None
    status: Optional[Boleto.Status] = None

    @field_validator('installment', mode='before')
    @classmethod
    def extract_installment_id(cls, v):
        if isinstance(v, dict) and 'id' in v:
            return v['id']
        return v


class BoletoOutSchema(OutSchema):
    pdf: str
    status: Boleto.Status

    @field_validator('pdf', mode='before')
    @classmethod
    def get_pdf_url(cls, v: Any) -> str:
        return v.url if hasattr(v, 'url') else str(v)
