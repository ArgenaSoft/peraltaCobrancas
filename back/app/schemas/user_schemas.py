from datetime import datetime
from ninja import Schema


class UserInSchema(Schema):
    cpf: str
    is_active: bool


class UserOutSchema(Schema):
    id: int
    cpf: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserGetCodeSchema(Schema):
    cpf: str
    phone: str
