
from app.models import ApiConsumer
from app.repositories import BaseRepository


class ApiConsumerRepository(BaseRepository[ApiConsumer]):
    model = ApiConsumer
