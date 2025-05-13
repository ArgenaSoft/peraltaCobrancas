from datetime import datetime
from typing import Optional
from ninja import Schema

from app.schemas.user_schemas import UserOutSchema


class PayerInSchema(Schema):
    cpf: str
    name: str
    phone: str


class PayerPatchInSchema(Schema):
    cpf: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None


class PayerOutSchema(Schema):
    user: UserOutSchema
    name: str
    phone: str
    created_at: datetime
    updated_at: datetime
