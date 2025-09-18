from datetime import datetime
from typing import Optional

from app.schemas import BaseSchema, OutSchema
from app.schemas.user_schemas import UserOutSchema


class PayerInSchema(BaseSchema):
    cpf_cnpj: str
    name: str
    phone: str


class PayerPatchInSchema(BaseSchema):
    cpf_cnpj: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None


class PayerOutSchema(OutSchema):
    user: UserOutSchema
    name: str
    phone: str
    created_at: datetime
    updated_at: datetime
