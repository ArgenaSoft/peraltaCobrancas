from datetime import datetime

from app.schemas import BaseSchema, OutSchema
from app.models import User

class AdminInSchema(BaseSchema):
    cpf_cnpj: str
    is_active: bool = True
    staff_level: str = User.StaffLevel.ADMIN

class UserInSchema(BaseSchema):
    cpf_cnpj: str
    is_active: bool


class UserOutSchema(OutSchema):
    cpf_cnpj: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserGetCodeSchema(BaseSchema):
    cpf_cnpj: str
    phone: str


class UserWaitToGetCodeSchema(BaseSchema):
    wait_time_seconds: float


class UserShortOutSchema(OutSchema):
    id: int
    cpf_cnpj: str