from datetime import datetime
from types import SimpleNamespace
from typing import ClassVar, Dict, List, Optional, Type

from ninja import Schema
from django.core.paginator import Paginator, Page
from pydantic import field_serializer


class ErrorSchema(Schema):
    code: int
    message: str
    data: Optional[Dict] = None


class ListSchema(Schema):
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    filters: Optional[dict] = None
    search: Optional[str] = None
    
    def filters(self) -> Dict:
        return {
            'filters': self.filters,
            'search': self.search
        }


class PaginatedOutSchema(Schema):
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


class UserInSchema(Schema):
    cpf: str
    is_active: bool


class UserOutSchema(Schema):
    id: int
    cpf: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserGetCodeSchema(Schema):
    cpf: str
    phone: str


class PayerInSchema(Schema):
    cpf: str
    name: str
    phone: str


class PayerPatchInSchema(Schema):
    cpf: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None


class PayerOutSchema(Schema):
    user: UserOutSchema
    name: str
    phone: str
    created_at: datetime
    updated_at: datetime


class LoginSchema(Schema):
    cpf: str
    phone: str
    code: str


class TokenOutSchema(Schema):
    access: str
    refresh: str


class RefreshInputSchema(Schema):
    refresh: str


class RefreshPairSchema(Schema):
    access: str
    refresh: str


class UserSchema:
    In = UserInSchema
    Out = UserOutSchema
    GetCode = UserGetCodeSchema

class PayerSchema:
    In = PayerInSchema
    PatchIn = PayerPatchInSchema
    Out = PayerOutSchema
