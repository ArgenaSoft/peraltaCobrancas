from typing import Generic, List, TypeVar

from django.db.models import Model
from ninja import Schema
from app.repositories import BaseRepository

RepositoryT = TypeVar("RepositoryT", bound=BaseRepository)
ModelT = TypeVar("ModelT", bound=Model)


class BaseController(Generic[RepositoryT, ModelT]):
    REPOSITORY: RepositoryT = None
    MODEL: ModelT = None

    @classmethod
    def update(cls, id: int, schema: Schema) -> ModelT:
        instance = cls.REPOSITORY.get(pk=id)
        return cls.REPOSITORY.update(instance, **schema.model_dump(exclude_none=True))

    @classmethod
    def get(cls, *args, **kwargs) -> List[ModelT]:
        return cls.REPOSITORY.get(*args, **kwargs)

    @classmethod
    def delete(cls, *args, **kwargs) -> None:
        instance: ModelT = cls.REPOSITORY.get(*args, **kwargs)
        return cls.REPOSITORY.delete(instance)
