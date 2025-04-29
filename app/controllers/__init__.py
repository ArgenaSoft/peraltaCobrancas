from typing import Dict, Generic, List, TypeVar, Type

from django.db.models import Model
from ninja import Schema
from app.repositories import BaseRepository
from app.schemas import BaseSchema

RepositoryT = TypeVar("RepositoryT", bound=BaseRepository)
SchemaT = TypeVar("SchemaT", bound=Type[BaseSchema])
ModelT = TypeVar("ModelT", bound=Model)


class BaseController(Generic[RepositoryT, SchemaT, ModelT]):
    REPOSITORY: RepositoryT = None
    SCHEMA: SchemaT = None
    MODEL: ModelT = None

    @classmethod
    def update(cls, id: int, schema: Schema) -> ModelT:
        instance = cls.REPOSITORY.get(pk=id)
        return cls.REPOSITORY.update(instance, **schema.model_dump(exclude_none=True))

    @classmethod
    def get(cls, *args, **kwargs) -> List[ModelT]:
        return cls.REPOSITORY.get(*args, **kwargs)
