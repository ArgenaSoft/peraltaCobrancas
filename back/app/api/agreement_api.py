import json
import logging
from typing import Dict

from django.core.handlers.wsgi import WSGIRequest
from ninja import Query, Router
from ninja.responses import codes_4xx

from app.api import endpoint
from app.controllers.agreement_controller import AgreementController
from app.models import Agreement
from app.schemas import DeleteSchema, ErrorSchema, ListSchema, PaginatedOutSchema
from app.schemas.agreement_schemas import AgreementInSchema, AgreementOutSchema, AgreementPatchInSchema

agreement_router = Router()
lgr = logging.getLogger(__name__)


@agreement_router.post('/', response={201: AgreementOutSchema, codes_4xx: ErrorSchema})
@endpoint
def create_agreement(request: WSGIRequest, data: AgreementInSchema):
    new_agreement: Agreement = AgreementController.create(data)
    return new_agreement, 201


@agreement_router.get('/{int:agreement_id}', response={200: AgreementOutSchema})
@endpoint
def view_agreement(request: WSGIRequest, agreement_id: int):
    agreement: Agreement = AgreementController.get(id=agreement_id)
    return agreement, 200


@agreement_router.patch('/{int:agreement_id}', response={200: AgreementOutSchema})
@endpoint
def edit_agreement(request: WSGIRequest, agreement_id: int, schema: AgreementPatchInSchema):
    agreement: Agreement = AgreementController.update(agreement_id, schema)
    return agreement, 200


@agreement_router.get('/', response={200: PaginatedOutSchema})
@endpoint
def list_agreement(request: WSGIRequest, data: Query[ListSchema]):
    agreements_page, paginator = AgreementController.filter(data)
    return {
        "page": agreements_page,
        "paginator": paginator,
    }, 200


@agreement_router.delete('/{int:agreement_id}', response={200: DeleteSchema})
@endpoint
def delete_payer(request: WSGIRequest, agreement_id: int):
    AgreementController.delete(id=agreement_id)
    return {"message": "Acordo deletado!"}, 200
