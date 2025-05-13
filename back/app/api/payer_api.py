import logging

from django.core.handlers.wsgi import WSGIRequest
from ninja import Query, Router
from ninja.responses import codes_4xx

from app.api import endpoint
from app.controllers.payer_controller import PayerController
from app.models import Payer
from app.schemas import DeleteSchema, ErrorSchema, ListSchema, PaginatedOutSchema
from app.schemas.payer_schemas import PayerInSchema, PayerOutSchema, PayerPatchInSchema

payer_router = Router()
lgr = logging.getLogger(__name__)


@payer_router.post('/', response={201: PayerOutSchema, codes_4xx: ErrorSchema})
@endpoint
def create_payer(request: WSGIRequest, data: PayerInSchema):
    new_payer: Payer = PayerController.create(data)
    return new_payer, 201


@payer_router.get('/{int:payer_id}', response={200: PayerOutSchema})
@endpoint
def view_payer(request: WSGIRequest, payer_id: int):
    payer: Payer = PayerController.get(id=payer_id)
    return payer, 200


@payer_router.patch('/{int:payer_id}', response={200: PayerOutSchema})
@endpoint
def edit_payer(request: WSGIRequest, payer_id: int, data: PayerPatchInSchema):
    payer: Payer = PayerController.update(payer_id, data)
    return payer, 200


@payer_router.get('/', response={200: PaginatedOutSchema})
@endpoint
def list_payer(request: WSGIRequest, data: Query[ListSchema]):
    payers_page, paginator = PayerController.filter(data)
    return {
        "page": payers_page,
        "paginator": paginator,
    }, 200

@payer_router.delete('/{int:payer_id}', response={200: DeleteSchema})
@endpoint
def delete_payer(request: WSGIRequest, payer_id: int):
    PayerController.delete(id=payer_id)
    return {"message": "Pagador deletado!"}, 200
