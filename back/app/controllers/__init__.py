from typing import Generic, List, Tuple, Type, TypeVar

from django.core.paginator import Paginator, Page
from django.db.models import Model, QuerySet
from ninja import Schema

from app.repositories import BaseRepository
from app.schemas import ListSchema

RepositoryT = TypeVar("RepositoryT", bound=BaseRepository)
ModelT = TypeVar("ModelT", bound=Model)

class BaseController(Generic[RepositoryT, ModelT]):
    REPOSITORY: Type[RepositoryT] = None
    MODEL: Type[ModelT] = None

    @classmethod
    def update(cls, id: int, schema: Schema) -> ModelT:
        instance = cls.REPOSITORY.get(pk=id)
        return cls.REPOSITORY.update(instance, **schema.model_dump())

    @classmethod
    def get(cls, *args, **kwargs) -> ModelT:
        return cls.REPOSITORY.get(*args, **kwargs)

    @classmethod
    def delete(cls, *args, **kwargs) -> None:
        instance: ModelT = cls.REPOSITORY.get(*args, **kwargs)
        return cls.REPOSITORY.delete(instance)

    @classmethod
    def filter_paginated(cls, schema: ListSchema) -> Tuple[Page, Paginator]:
        """
        Lista instâncias com base nos filtros fornecidos.

        Parâmetros:
            - schema: Filtros de paginação e pesquisa.

        Retorna:
            - List[ModelT]: Lista de instancias.
        """
        instances = cls.REPOSITORY.filter(**schema.filters, include_rels=schema.include_rels)
        instances = instances.order_by('updated_at')
        paginator = Paginator(instances, schema.page_size)
        page_number = schema.page

        paginated: Page = paginator.get_page(page_number)
        return paginated, paginator

    @classmethod
    def filter(cls, *args, **kwargs) -> QuerySet[ModelT]:
        """
        Lista instâncias com base nos filtros fornecidos.

        Retorna:
            - List[ModelT]: Lista de instancias.
        """
        return cls.REPOSITORY.filter(*args, **kwargs)
