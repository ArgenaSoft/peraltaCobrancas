import logging

from ninja import Query

from app.api import CustomRouter, endpoint
from app.controllers.creditor_controller import CreditorController
from app.models import Creditor
from app.schemas import ReturnSchema, ListSchema, PaginatedOutSchema
from app.schemas.creditor_schemas import CreditorInSchema, CreditorOutSchema, CreditorPatchInSchema
from core.custom_request import CustomRequest


creditor_router = CustomRouter(tags=["Credores"])
lgr = logging.getLogger(__name__)


@creditor_router.post('/', response={201: ReturnSchema[CreditorOutSchema]})
@endpoint("Criar credor")
def create_creditor(request: CustomRequest, data: CreditorInSchema):
    new_creditor: Creditor = CreditorController.create(data)
    return ReturnSchema(code=201, data=new_creditor)


@creditor_router.get('/{int:creditor_id}', response={200: ReturnSchema[CreditorOutSchema]})
@endpoint("Visualizar credor")
def view_creditor(request: CustomRequest, creditor_id: int):
    creditor: Creditor = CreditorController.get(id=creditor_id)
    return ReturnSchema(code=200, data=creditor)


@creditor_router.patch('/{int:creditor_id}', response={200: ReturnSchema[CreditorOutSchema]})
@endpoint("Editar credor")
def edit_creditor(request: CustomRequest, creditor_id: int, data: CreditorPatchInSchema):
    creditor: Creditor = CreditorController.update(creditor_id, data)
    return ReturnSchema(code=200, data=creditor)


@creditor_router.get('/', response={200: ReturnSchema[PaginatedOutSchema[CreditorOutSchema]]})
@endpoint("Listar credores")
def list_creditor(request: CustomRequest, data: Query[ListSchema]):
    data.build_filters_from_query(request.GET.dict())
    creditors_page, paginator = CreditorController.filter_paginated(data)
    return ReturnSchema(
        code=200, 
        data=PaginatedOutSchema.build(creditors_page, paginator)
    )


@creditor_router.delete('/{int:creditor_id}', response={200: ReturnSchema})
@endpoint(None)
def delete_creditor(request: CustomRequest, creditor_id: int):
    lgr.info(f"Ator {request.actor.identification} (ID: {request.actor.id}) está deletando o credor {creditor_id}")
    CreditorController.delete(id=creditor_id)
    return ReturnSchema(code=200)
