from typing import Optional
import logging

from ninja import File, Form, Query, UploadedFile

from app.api import CustomRouter, endpoint
from app.controllers.boleto_controller import BoletoController
from app.exceptions import HttpFriendlyException
from app.models import Boleto
from app.schemas import ReturnSchema, ListSchema, PaginatedOutSchema
from app.schemas.boleto_schemas import BoletoInSchema, BoletoOutSchema, BoletoPatchInSchema
from core.auth import AllowHumansAuth
from core.custom_request import CustomRequest

boleto_router = CustomRouter(tags=["Boletos"])
lgr = logging.getLogger(__name__)


@boleto_router.post('/', response={201: ReturnSchema[BoletoOutSchema]})
@endpoint("Criar boleto")
def create_boleto(
    request: CustomRequest,
    pdf: UploadedFile = File(...),
    installment: int = Form(...),
    status: Boleto.Status = Form(...)
):
    data = BoletoInSchema(
        pdf=pdf,
        installment=installment,
        status=status,)

    new_boleto: Boleto = BoletoController.create(data)
    return ReturnSchema(code=201, data=new_boleto)


@boleto_router.get('/{int:boleto_id}', response={200: ReturnSchema[BoletoOutSchema]})
@endpoint("Visualizar boleto")
def view_boleto(request: CustomRequest, boleto_id: int):
    boleto: Boleto = BoletoController.get(id=boleto_id)
    if request.actor.is_human and boleto.installment.agreement.payer.user.id != request.actor.id:
        raise HttpFriendlyException(403, "Você não tem permissão para acessar esse boleto")
    return ReturnSchema(code=200, data=boleto)


# Precisa ser POST por causa do envio de arquivo
@boleto_router.post('/{int:boleto_id}', response={200: ReturnSchema[BoletoOutSchema]})
@endpoint("Editar boleto")
def edit_boleto(
    request: CustomRequest,
    boleto_id: int,
    pdf: Optional[UploadedFile] = File(None),
    installment: Optional[int] = Form(None),
    status: Optional[Boleto.Status] = Form(None)
):
    data = BoletoPatchInSchema(
        pdf=pdf,
        installment=installment,
        status=status)
    boleto: Boleto = BoletoController.update(boleto_id, data)
    return ReturnSchema(code=200, data=boleto)


@boleto_router.get('/', response={200: ReturnSchema[PaginatedOutSchema[BoletoOutSchema]]}, auth=AllowHumansAuth())
@endpoint("Listar boletos")
def list_boleto(request: CustomRequest, data: Query[ListSchema]):
    data.build_filters_from_query(request.GET.dict())

    if request.actor.is_human:
        data.filters['installment__agreement__payer__user_id'] = request.actor.id

    boletos_page, paginator = BoletoController.filter_paginated(data)

    return ReturnSchema(
        code=200, 
        data=PaginatedOutSchema.build(boletos_page, paginator)
    )


@boleto_router.delete('/{int:boleto_id}', response={200: ReturnSchema})
@endpoint(None)
def delete_payer(request: CustomRequest, boleto_id: int):
    lgr.info(f"Ator {request.actor.identification} (ID: {request.actor.id}) está deletando o boleto {boleto_id}")
    BoletoController.delete(id=boleto_id)
    return ReturnSchema(code=200)
