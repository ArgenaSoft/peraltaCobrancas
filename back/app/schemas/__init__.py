from typing import Annotated, Dict, Generic, List, Optional, TypeVar

from ninja import Schema
from django.core.paginator import Paginator, Page
from pydantic import BeforeValidator, ConfigDict, field_serializer

from app.exceptions import HttpFriendlyException


class BaseSchema(Schema):
    """
        Classe base para todos os schemas.
    """
    model_config = ConfigDict(extra='ignore', arbitrary_types_allowed = True)

    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs, exclude_none=True)


class ListSchema(BaseSchema):
    page: int = 1
    page_size: int = 10
    filters: dict = {}
    search: Optional[str] = None


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
