from datetime import datetime

from app.schemas import BaseSchema, OutSchema


class UserInSchema(BaseSchema):
    cpf: str
    is_active: bool


class UserOutSchema(OutSchema):
    cpf: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserGetCodeSchema(BaseSchema):
    cpf: str
    phone: str


class UserWaitToGetCodeSchema(BaseSchema):
    wait_time_seconds: float


class UserShortOutSchema(OutSchema):
    id: int
    cpf: str