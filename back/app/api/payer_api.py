import logging

from ninja import Query
from ninja.responses import codes_4xx

from app.api import CustomRouter, endpoint
from app.controllers.payer_controller import PayerController
from app.exceptions import HttpFriendlyException
from app.models import Payer
from app.schemas import DeleteSchema, ErrorSchema, ListSchema, PaginatedOutSchema
from app.schemas.payer_schemas import PayerInSchema, PayerOutSchema, PayerPatchInSchema
from core.auth import AllowHumansAuth
from core.custom_request import CustomRequest

payer_router = CustomRouter()
lgr = logging.getLogger(__name__)


@payer_router.post('/', response={201: PayerOutSchema, codes_4xx: ErrorSchema})
@endpoint
def create_payer(request: CustomRequest, data: PayerInSchema):
    new_payer: Payer = PayerController.create(data)
    return new_payer, 201


@payer_router.get('/{int:payer_id}', response={200: PayerOutSchema}, auth=AllowHumansAuth())
@endpoint
def view_payer(request: CustomRequest, payer_id: int):
    payer: Payer = PayerController.get(id=payer_id)
    if request.actor.is_human and payer.user.id != request.actor.id:
        raise HttpFriendlyException(403, "Você não tem permissão para acessar esse pagador")

    return payer, 200


@payer_router.patch('/{int:payer_id}', response={200: PayerOutSchema})
@endpoint
def edit_payer(request: CustomRequest, payer_id: int, data: PayerPatchInSchema):
    payer: Payer = PayerController.update(payer_id, data)
    return payer, 200


@payer_router.get('/', response={200: PaginatedOutSchema})
@endpoint
def list_payer(request: CustomRequest, data: Query[ListSchema]):
    payers_page, paginator = PayerController.filter(data)
    return PaginatedOutSchema.build(payers_page, paginator), 200



@payer_router.delete('/{int:payer_id}', response={200: DeleteSchema})
@endpoint
def delete_payer(request: CustomRequest, payer_id: int):
    PayerController.delete(id=payer_id)
    return {"message": "Pagador deletado!"}, 200
