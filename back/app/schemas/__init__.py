from typing import Annotated, Dict, Optional

from ninja import Schema
from django.core.paginator import Paginator, Page
from pydantic import BeforeValidator, ConfigDict, field_serializer


class BaseSchema(Schema):
    """
        Classe base para todos os schemas.
    """
    model_config = ConfigDict(extra='ignore', arbitrary_types_allowed = True)

    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs, exclude_none=True)
        

class ErrorSchema(BaseSchema):
    code: int
    message: str
    data: Optional[Dict] = None


class ListSchema(BaseSchema):
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    filters: Optional[dict] = {}
    search: Optional[str] = None


class DeleteSchema(BaseSchema):
    message: str = "Deleted successfully!"
    data: Optional[Dict] = None


class PaginatorSchema(BaseSchema):
    page_size: int
    total_pages: int
    total_items: int


class PageSchema(BaseSchema):
    page: int
    items: list


class PaginatedOutSchema(BaseSchema):
    paginator: PaginatorSchema
    page: PageSchema

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
                items=[i.dict() for i in page.object_list ]
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
