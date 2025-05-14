from typing import Annotated, Dict, Optional

from ninja import Schema
from django.core.paginator import Paginator, Page
from pydantic import BeforeValidator, ConfigDict, field_serializer


class BaseSchema(Schema):
    """
        Classe base para todos os schemas.
    """
    model_config = ConfigDict(extra='ignore', arbitrary_types_allowed = True)

class ErrorSchema(BaseSchema):
    code: int
    message: str
    data: Optional[Dict] = None


class ListSchema(BaseSchema):
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    filters: Optional[dict] = None
    search: Optional[str] = None
    
    def filters(self) -> Dict:
        return {
            'filters': self.filters,
            'search': self.search
        }


class DeleteSchema(BaseSchema):
    message: str = "Deleted successfully!"
    data: Optional[Dict] = None


class PaginatedOutSchema(BaseSchema):
    paginator: Paginator
    page: Page

    @field_serializer('paginator')
    def serialize_paginator(self, paginator: Paginator) -> Dict:
        return {
            "page_size": paginator.per_page,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count
        }

    @field_serializer('page')
    def serialize_page(self, page: Page) -> Dict:
        return {
            "page": page.number,
            "items": [i.dict() for i in page.object_list ]
        }

OptionalStrNotEmpty = Annotated[
    Optional[str],
    BeforeValidator(lambda v: None if isinstance(v, str) and v.strip() == "" else v)
]

StrNotEmpty = Annotated[
    str,
    BeforeValidator(lambda v: None if isinstance(v, str) and v.strip() == "" else v)
]
