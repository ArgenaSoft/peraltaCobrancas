import logging

from django.core.handlers.wsgi import WSGIRequest
from ninja import Query, Router
from ninja.responses import codes_4xx

from app.api import endpoint
from app.controllers.boleto_controller import BoletoController
from app.models import Boleto
from app.schemas import DeleteSchema, ErrorSchema, ListSchema, PaginatedOutSchema
from app.schemas.boleto_schemas import BoletoInSchema, BoletoOutSchema, BoletoPatchInSchema

boleto_router = Router()
lgr = logging.getLogger(__name__)


@boleto_router.post('/', response={201: BoletoOutSchema, codes_4xx: ErrorSchema})
@endpoint
def create_boleto(request: WSGIRequest, data: BoletoInSchema):
    new_boleto: Boleto = BoletoController.create(data)
    return new_boleto, 201


@boleto_router.get('/{int:boleto_id}', response={200: BoletoOutSchema})
@endpoint
def view_boleto(request: WSGIRequest, boleto_id: int):
    boleto: Boleto = BoletoController.get(id=boleto_id)
    return boleto, 200


@boleto_router.patch('/{int:boleto_id}', response={200: BoletoOutSchema})
@endpoint
def edit_boleto(request: WSGIRequest, boleto_id: int, schema: BoletoPatchInSchema):
    boleto: Boleto = BoletoController.update(boleto_id, schema)
    return boleto, 200


@boleto_router.get('/', response={200: PaginatedOutSchema})
@endpoint
def list_boleto(request: WSGIRequest, data: Query[ListSchema]):
    boletos_page, paginator = BoletoController.filter(data)
    return {
        "page": boletos_page,
        "paginator": paginator,
    }, 200


@boleto_router.delete('/{int:boleto_id}', response={200: DeleteSchema})
@endpoint
def delete_payer(request: WSGIRequest, boleto_id: int):
    BoletoController.delete(id=boleto_id)
    return {"message": "Boleto deletado!"}, 200
