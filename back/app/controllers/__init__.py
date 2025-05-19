from typing import Generic, List, Tuple, TypeVar

from django.core.paginator import Paginator, Page
from django.db.models import Model
from ninja import Schema

from app.repositories import BaseRepository
from app.schemas import ListSchema

RepositoryT = TypeVar("RepositoryT", bound=BaseRepository)
ModelT = TypeVar("ModelT", bound=Model)


class BaseController(Generic[RepositoryT, ModelT]):
    REPOSITORY: RepositoryT = None
    MODEL: ModelT = None

    @classmethod
    def update(cls, id: int, schema: Schema) -> ModelT:
        instance = cls.REPOSITORY.get(pk=id)
        return cls.REPOSITORY.update(instance, **schema.model_dump())

    @classmethod
    def get(cls, *args, **kwargs) -> List[ModelT]:
        return cls.REPOSITORY.get(*args, **kwargs)

    @classmethod
    def delete(cls, *args, **kwargs) -> None:
        instance: ModelT = cls.REPOSITORY.get(*args, **kwargs)
        return cls.REPOSITORY.delete(instance)

    @classmethod
    def filter(cls, schema: ListSchema) -> Tuple[Page, Paginator]:
        """
        Lista instâncias com base nos filtros fornecidos.

        Parâmetros:
            - schema: Filtros de paginação e pesquisa.

        Retorna:
            - List[Agreement]: Lista de instancias.
        """
        instances = cls.REPOSITORY.filter(**schema.filters)
        paginator = Paginator(instances, schema.page_size)
        page_number = schema.page

        instances: Page = paginator.get_page(page_number)
        return instances, paginator
