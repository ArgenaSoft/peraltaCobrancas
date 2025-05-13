
from ninja import Schema


class LoginSchema(Schema):
    cpf: str
    phone: str
    code: str


class TokenOutSchema(Schema):
    access: str
    refresh: str
    username: str


class RefreshInputSchema(Schema):
    refresh: str


class RefreshPairSchema(Schema):
    access: str
    refresh: str
