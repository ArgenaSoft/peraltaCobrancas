from typing import Annotated, Any, Dict, Generic, List, Optional, TypeVar

from ninja import FilterSchema, Schema
from ninja.schema import DjangoGetter

from django.core.paginator import Paginator, Page
from pydantic import BeforeValidator, ConfigDict, field_serializer, model_validator

from app.exceptions import HttpFriendlyException


class ExcludesNone(Schema):
    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs, exclude_none=True)


class BaseSchema(ExcludesNone):
    """
        Classe base para todos os schemas.
    """
    model_config = ConfigDict(extra='ignore', arbitrary_types_allowed = True)


class ListSchema(ExcludesNone):
    model_config = ConfigDict(extra='allow', arbitrary_types_allowed = True)
    page: int = 1
    page_size: int = 10
    # Relacionamentos a serem incluídos na busca
    include_rels: Optional[List[str]] = None
    filters: Dict[str, Any] = {}

    def build_filters_from_query(self, query: Dict) -> None:
        """
            Constrói os filtros a partir de um dicionário de query. 
            Feito para importar os filtros da requisição GET.

            Os filtros devem começar com 'f_'
        """

        self.filters = {}
        for key, value in query.items():
            if key.startswith('f_'):
                # Remove o prefixo 'f_' e adiciona ao dicionário de filtros
                self.filters[key[2:]] = value




class DeleteSchema(BaseSchema):
    message: str = "Deleted successfully!"
    data: Optional[Dict] = None


class PaginatorSchema(BaseSchema):
    page_size: int
    total_pages: int
    total_items: int


T = TypeVar('T')
class ReturnSchema(BaseSchema, Generic[T]):
    """
        Retorno padrão para todas as rotas.
    """
    code: int
    message: Optional[str] = None
    data: Optional[T] = None
    
    @classmethod
    def from_http_friendly_exception(cls, e: HttpFriendlyException):
        return cls(message=e.message, code=e.code, data=e.data)


class PageSchema(BaseSchema, Generic[T]):
    page: int
    items: List[T]


class PaginatedOutSchema(BaseSchema, Generic[T]):
    paginator: PaginatorSchema
    page: PageSchema[T]

    @classmethod
    def build(cls, page: Page, paginator: Paginator):
        return cls(
            paginator=PaginatorSchema(
                page_size=paginator.per_page,
                total_pages=paginator.num_pages,
                total_items=paginator.count
            ),
            page=PageSchema(
                page=page.number,
                items=page.object_list
            )
        )


class OutSchema(BaseSchema):
    id: int


OptionalStrNotEmpty = Annotated[
    Optional[str],
    BeforeValidator(lambda v: None if isinstance(v, str) and v.strip() == "" else v)
]


StrNotEmpty = Annotated[
    str,
    BeforeValidator(lambda v: None if isinstance(v, str) and v.strip() == "" else v)
]
