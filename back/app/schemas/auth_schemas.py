from app.schemas import BaseSchema


class LoginSchema(BaseSchema):
    cpf_cnpj: str
    phone: str
    code: str


class TokenOutSchema(BaseSchema):
    access: str
    refresh: str
    username: str


class RefreshInputSchema(BaseSchema):
    refresh: str


class RefreshPairSchema(BaseSchema):
    access: str
    refresh: str
