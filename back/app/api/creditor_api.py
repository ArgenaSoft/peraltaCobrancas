import logging

from ninja import Query
from ninja.responses import codes_4xx

from app.api import CustomRouter, endpoint
from app.controllers.creditor_controller import CreditorController
from app.models import Creditor
from app.schemas import DeleteSchema, ErrorSchema, ListSchema, PaginatedOutSchema
from app.schemas.creditor_schemas import CreditorInSchema, CreditorOutSchema, CreditorPatchInSchema
from core.custom_request import CustomRequest


creditor_router = CustomRouter()
lgr = logging.getLogger(__name__)


@creditor_router.post('/', response={201: CreditorOutSchema, codes_4xx: ErrorSchema})
@endpoint
def create_creditor(request: CustomRequest, data: CreditorInSchema):
    new_creditor: Creditor = CreditorController.create(data)
    return new_creditor, 201


@creditor_router.get('/{int:creditor_id}', response={200: CreditorOutSchema})
@endpoint
def view_creditor(request: CustomRequest, creditor_id: int):
    creditor: Creditor = CreditorController.get(id=creditor_id)
    return creditor, 200


@creditor_router.patch('/{int:creditor_id}', response={200: CreditorOutSchema})
@endpoint
def edit_creditor(request: CustomRequest, creditor_id: int, data: CreditorPatchInSchema):
    creditor: Creditor = CreditorController.update(creditor_id, data)
    return creditor, 200


@creditor_router.get('/', response={200: PaginatedOutSchema})
@endpoint
def list_creditor(request: CustomRequest, data: Query[ListSchema]):
    creditors_page, paginator = CreditorController.filter(data)
    return PaginatedOutSchema.build(creditors_page, paginator), 200



@creditor_router.delete('/{int:creditor_id}', response={200: DeleteSchema})
@endpoint
def delete_payer(request: CustomRequest, creditor_id: int):
    CreditorController.delete(id=creditor_id)
    return {"message": "Credor deletado!"}, 200
