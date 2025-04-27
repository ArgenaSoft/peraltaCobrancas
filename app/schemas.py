from datetime import datetime
from typing import Optional
from ninja import Schema

class UserSchema:
    class In(Schema):
        cpf: str
        is_active: bool

    class Out(Schema):
        id: int
        cpf: str
        is_active: bool
        created_at: datetime
        updated_at: datetime

class PayerSchema:
    class In(Schema):
        cpf: str
        name: str
        phone: str

    class PatchIn(Schema):
        cpf: Optional[str] = None
        name: Optional[str] = None
        phone: Optional[str] = None

    class Out(Schema):
        user: UserSchema.Out
        name: str
        phone: str
        created_at: datetime
        updated_at: datetime