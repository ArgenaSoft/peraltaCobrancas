from datetime import datetime
from typing import Dict, List, Optional

from ninja import Schema
from django.core.paginator import Paginator, Page
from pydantic import field_serializer

class BaseSchema:
    class Error(Schema):
        code: int
        message: str

    class List(Schema):
        page: Optional[int] = 1
        page_size: Optional[int] = 10
        filters: Optional[dict] = None
        search: Optional[str] = None
        
        def filters(self) -> Dict:
            return {
                'filters': self.filters,
                'search': self.search
            }


    class PaginatedOut(Schema):
        class Config:
            arbitrary_types_allowed = True

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

    class PatchIn(Schema):
        # Deverá ser sobrescrito
        pass

    class In(Schema):
        # Deverá ser sobrescrito
        pass

    class Out(Schema):
        # Deverá ser sobrescrito
        pass


class UserSchema(BaseSchema):
    class In(Schema):
        cpf: str
        is_active: bool

    class Out(Schema):
        id: int
        cpf: str
        is_active: bool
        created_at: datetime
        updated_at: datetime


class PayerSchema(BaseSchema):
    class In(Schema):
        cpf: str
        name: str
        phone: str

    class PatchIn(Schema):
        cpf: Optional[str] = None
        name: Optional[str] = None
        phone: Optional[str] = None

    class Out(Schema):
        user: UserSchema.Out
        name: str
        phone: str
        created_at: datetime
        updated_at: datetime

class UserSchema(BaseSchema):
    class GetCode(Schema):
        cpf: str
        phone: str

class AuthSchema(BaseSchema):
    class AuthInput(Schema):
        cpf: str
        phone: str
        code: str

    class TokenOut(Schema):
        access: str
        refresh: str

    class RefreshInput(Schema):
        refresh: str

    class TokenPair(Schema):
        access: str
        refresh: str
