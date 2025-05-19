from typing import Optional
import datetime
import logging

from ninja import File, Form, Query, UploadedFile
from ninja.responses import codes_4xx, codes_5xx

from app.api import CustomRouter, endpoint
from app.controllers.boleto_controller import BoletoController
from app.exceptions import HttpFriendlyException
from app.models import Boleto
from app.schemas import DeleteSchema, ErrorSchema, ListSchema, PaginatedOutSchema
from app.schemas.boleto_schemas import BoletoInSchema, BoletoOutSchema, BoletoPatchInSchema
from core.auth import AllowHumansAuth
from core.custom_request import CustomRequest

boleto_router = CustomRouter()
lgr = logging.getLogger(__name__)


@boleto_router.post('/', response={201: BoletoOutSchema, codes_4xx: ErrorSchema})
@endpoint
def create_boleto(
    request: CustomRequest,
    pdf: UploadedFile = File(...),
    installment: int = Form(...),
    status: Boleto.Status = Form(...),
    due_date: datetime.date = Form(...)
):
    data = BoletoInSchema(
        pdf=pdf,
        installment=installment,
        status=status,
        due_date=due_date,)

    new_boleto: Boleto = BoletoController.create(data)
    return new_boleto, 201


@boleto_router.get('/{int:boleto_id}', response={200: BoletoOutSchema, 404: BoletoOutSchema})
@endpoint
def view_boleto(request: CustomRequest, boleto_id: int):
    boleto: Boleto = BoletoController.get(id=boleto_id)
    if request.actor.is_human and boleto.installment.agreement.payer.user.id != request.actor.id:
        raise HttpFriendlyException(403, "Você não tem permissão para acessar esse boleto")
    return boleto, 200


# Precisa ser POST por causa do envio de arquivo
@boleto_router.post('/{int:boleto_id}', response={200: BoletoOutSchema, codes_4xx: ErrorSchema, codes_5xx: ErrorSchema})
@endpoint
def edit_boleto(
    request: CustomRequest,
    boleto_id: int,
    pdf: Optional[UploadedFile] = File(None),
    installment: Optional[int] = Form(None),
    status: Optional[Boleto.Status] = Form(None),
    due_date: Optional[datetime.date] = Form(None)
):
    data = BoletoPatchInSchema(
        pdf=pdf,
        installment=installment,
        status=status,
        due_date=due_date,)
    boleto: Boleto = BoletoController.update(boleto_id, data)
    return boleto, 200


@boleto_router.get('/', response={200: PaginatedOutSchema, codes_4xx: ErrorSchema}, auth=AllowHumansAuth())
@endpoint
def list_boleto(request: CustomRequest, data: Query[ListSchema]):
    if request.actor.is_human:
        filters = {
            'installment__agreement__payer__user_id': request.actor.id,
        }
        data.filters.update(filters)

    boletos_page, paginator = BoletoController.filter(data)

    return PaginatedOutSchema.build(boletos_page, paginator), 200


@boleto_router.delete('/{int:boleto_id}', response={200: DeleteSchema})
@endpoint
def delete_payer(request: CustomRequest, boleto_id: int):
    BoletoController.delete(id=boleto_id)
    return {"message": "Boleto deletado!"}, 200
