import logging

from django.core.handlers.wsgi import WSGIRequest
from ninja import Query, Router
from ninja.responses import codes_4xx

from app.api import endpoint
from app.controllers.creditor_controller import CreditorController
from app.models import Creditor
from app.schemas import DeleteSchema, ErrorSchema, ListSchema, PaginatedOutSchema
from app.schemas.creditor_schemas import CreditorInSchema, CreditorOutSchema, CreditorPatchInSchema


creditor_router = Router()
lgr = logging.getLogger(__name__)


@creditor_router.post('/', response={201: CreditorOutSchema, codes_4xx: ErrorSchema})
@endpoint
def create_creditor(request: WSGIRequest, data: CreditorInSchema):
    new_creditor: Creditor = CreditorController.create(data)
    return new_creditor, 201


@creditor_router.get('/{int:creditor_id}', response={200: CreditorOutSchema})
@endpoint
def view_creditor(request: WSGIRequest, creditor_id: int):
    creditor: Creditor = CreditorController.get(id=creditor_id)
    return creditor, 200


@creditor_router.patch('/{int:creditor_id}', response={200: CreditorOutSchema})
@endpoint
def edit_creditor(request: WSGIRequest, creditor_id: int, data: CreditorPatchInSchema):
    creditor: Creditor = CreditorController.update(creditor_id, data)
    return creditor, 200


@creditor_router.get('/', response={200: PaginatedOutSchema})
@endpoint
def list_creditor(request: WSGIRequest, data: Query[ListSchema]):
    creditors_page, paginator = CreditorController.filter(data)
    return {
        "page": creditors_page,
        "paginator": paginator,
    }, 200


@creditor_router.delete('/{int:creditor_id}', response={200: DeleteSchema})
@endpoint
def delete_payer(request: WSGIRequest, creditor_id: int):
    CreditorController.delete(id=creditor_id)
    return {"message": "Credor deletado!"}, 200
