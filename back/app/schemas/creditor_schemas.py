from datetime import datetime
from typing import Optional
from ninja import Schema

class CreditorInSchema(Schema):
    name: str
    reissue_margin: int


class CreditorPatchInSchema(Schema):
    name: Optional[str] = None
    reissue_margin: Optional[int] = None


class CreditorOutSchema(Schema):
    name: str
    reissue_margin: int
    created_at: datetime
    updated_at: datetime
