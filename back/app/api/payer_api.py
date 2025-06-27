import logging

from ninja import Query

from app.api import CustomRouter, endpoint
from app.controllers.payer_controller import PayerController
from app.exceptions import HttpFriendlyException
from app.models import Payer
from app.schemas import DeleteSchema, ReturnSchema, ListSchema, PaginatedOutSchema
from app.schemas.payer_schemas import PayerInSchema, PayerOutSchema, PayerPatchInSchema
from core.auth import AllowHumansAuth
from core.custom_request import CustomRequest

payer_router = CustomRouter(tags=["Pagadores"])
lgr = logging.getLogger(__name__)


@payer_router.post('/', response={201: ReturnSchema[PayerOutSchema]})
@endpoint("Criar pagador")
def create_payer(request: CustomRequest, data: PayerInSchema):
    new_payer: Payer = PayerController.create(data)
    return ReturnSchema(code=201, data=new_payer)


@payer_router.get('/{int:payer_id}', response={200: ReturnSchema[PayerOutSchema]}, auth=AllowHumansAuth())
@endpoint("Visualizar pagador")
def view_payer(request: CustomRequest, payer_id: int):
    payer: Payer = PayerController.get(id=payer_id)
    if request.actor.is_human and payer.user.id != request.actor.id:
        raise HttpFriendlyException(403, "Você não tem permissão para acessar esse pagador")

    return ReturnSchema(code=200, data=payer)


@payer_router.patch('/{int:payer_id}', response={200: ReturnSchema[PayerOutSchema]})
@endpoint("Editar pagador")
def edit_payer(request: CustomRequest, payer_id: int, data: PayerPatchInSchema):
    payer: Payer = PayerController.update(payer_id, data)
    return ReturnSchema(code=200, data=payer)


@payer_router.get('/', response={200: ReturnSchema[PaginatedOutSchema[PayerOutSchema]]})
@endpoint("Listar pagadores")
def list_payer(request: CustomRequest, data: Query[ListSchema]):
    data.build_filters_from_query(request.GET.dict())

    payers_page, paginator = PayerController.filter_paginated(data)
    return ReturnSchema(
        code=200,
        data=PaginatedOutSchema.build(payers_page, paginator)
    )


@payer_router.delete('/{int:payer_id}', response={200: ReturnSchema[DeleteSchema]})
@endpoint(None)
def delete_payer(request: CustomRequest, payer_id: int):
    lgr.info(f"Ator {request.actor.identification} (ID: {request.actor.id}) está deletando o pagador {payer_id}")
    PayerController.delete(id=payer_id)
    return ReturnSchema(code=200, message="Pagador deletado!")
