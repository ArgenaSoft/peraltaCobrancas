from datetime import datetime
from typing import Optional

from app.schemas import BaseSchema

class CreditorInSchema(BaseSchema):
    name: str
    reissue_margin: int


class CreditorPatchInSchema(BaseSchema):
    name: Optional[str] = None
    reissue_margin: Optional[int] = None


class CreditorOutSchema(BaseSchema):
    name: str
    reissue_margin: int
    created_at: datetime
    updated_at: datetime
