from datetime import datetime

from app.schemas import OutSchema
from app.schemas.user_schemas import UserShortOutSchema

class LoginHistoryOutSchema(OutSchema):
    user: UserShortOutSchema
    timestamp: datetime
    phone_used: str
