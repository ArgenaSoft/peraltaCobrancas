import logging

from django.core.handlers.wsgi import WSGIRequest
from ninja import Query, Router
from ninja.responses import codes_4xx

from app.api import endpoint
from app.controllers.payer_controller import PayerController
from app.models import Payer
from app.schemas import PayerSchema

payer_router = Router()
lgr = logging.getLogger(__name__)


@payer_router.post('/', response={201: PayerSchema.Out, codes_4xx: PayerSchema.Error})
@endpoint
def create_payer(request: WSGIRequest, data: PayerSchema.In):
    new_payer: Payer = PayerController.create(data)
    return new_payer, 201


@payer_router.patch('/{int:payer_id}', response={200: PayerSchema.Out})
@endpoint
def edit_payer(request: WSGIRequest, payer_id: int, data: PayerSchema.PatchIn):
    payer: Payer = PayerController.update(payer_id, data)
    return payer, 200


@payer_router.get('/', response={200: PayerSchema.PaginatedOut})
@endpoint
def list_payer(request: WSGIRequest, data: Query[PayerSchema.List]):
    payers_page, paginator = PayerController.filter(data)
    return {
        "page": payers_page,
        "paginator": paginator,
    }, 200
