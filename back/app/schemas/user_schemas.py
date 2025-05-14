from datetime import datetime

from app.schemas import BaseSchema


class UserInSchema(BaseSchema):
    cpf: str
    is_active: bool


class UserOutSchema(BaseSchema):
    id: int
    cpf: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserGetCodeSchema(BaseSchema):
    cpf: str
    phone: str
