import logging
from typing import Dict, List

from ninja import Query

from app.api import CustomRouter, endpoint
from app.controllers.agreement_controller import AgreementController
from app.controllers.payer_controller import PayerController
from app.exceptions import HttpFriendlyException
from app.models import Agreement, Boleto, Installment
from app.schemas import ReturnSchema, ListSchema, PaginatedOutSchema
from app.schemas.agreement_schemas import AgreementHomeInSchema, AgreementInSchema, AgreementOutSchema, AgreementPatchInSchema
from core.auth import AllowHumansAuth
from core.custom_request import CustomRequest

agreement_router = CustomRouter(tags=["Acordos"])
lgr = logging.getLogger(__name__)


@agreement_router.post('/', response={201: ReturnSchema[AgreementOutSchema]})
@endpoint("Criar acordo")
def create_agreement(request: CustomRequest, data: AgreementInSchema):
    new_agreement: Agreement = AgreementController.create(data)
    return ReturnSchema(code=201, data=new_agreement)


@agreement_router.get('/{int:agreement_id}', response={200: ReturnSchema[AgreementOutSchema]})
@endpoint("Visualizar acordo")
def view_agreement(request: CustomRequest, agreement_id: int):
    agreement: Agreement = AgreementController.get(id=agreement_id)
    if request.actor.is_human and agreement.payer.user.id != request.actor.id:
        raise HttpFriendlyException(403, "Você não tem permissão para acessar esse acordo")

    return ReturnSchema(code=200, data=agreement)


@agreement_router.patch('/{int:agreement_id}', response={200: ReturnSchema[AgreementOutSchema]})
@endpoint("Editar acordo")
def edit_agreement(request: CustomRequest, agreement_id: int, schema: AgreementPatchInSchema):
    agreement: Agreement = AgreementController.update(agreement_id, schema)
    return ReturnSchema(code=200, data=agreement)


@agreement_router.get('/', response={200: ReturnSchema[PaginatedOutSchema[AgreementOutSchema]]}, auth=AllowHumansAuth())
@endpoint("Listar acordos")
def list_agreement(request: CustomRequest, data: Query[ListSchema]):
    data.build_filters_from_query(request.GET.dict())

    if request.actor.is_human:
        data.filters['payer__user_id'] = request.actor.id

    agreements_page, paginator = AgreementController.filter_paginated(data)
    return ReturnSchema(code=200, data=PaginatedOutSchema.build(agreements_page, paginator))


@agreement_router.delete('/{int:agreement_id}', response={200: ReturnSchema})
@endpoint(None)
def delete_payer(request: CustomRequest, agreement_id: int):
    lgr.info(f"Ator {request.actor.identification} (ID: {request.actor.id}) está deletando o acordo {agreement_id}")
    AgreementController.delete(id=agreement_id)

    return ReturnSchema(code=200)


@agreement_router.get('/home', response={200: ReturnSchema[List[Dict]]}, auth=AllowHumansAuth())
@endpoint("Listar acordos para a home")
def list_agreements_for_home(request: CustomRequest, data: Query[AgreementHomeInSchema]):
    if request.actor.is_human:
        user_id = request.actor.id
        payer = PayerController.get(user__id=user_id)
    else:
        if not data.payer_id:
            raise HttpFriendlyException(400, "Para acessar essa rota como um sistema, é necessário informar o id do Pagador")
        payer = PayerController.get(id=data.payer_id)

    agreements = AgreementController.filter(payer__id=payer.id, status=Agreement.Status.OPEN.value)
    output_data = []

    for agreement in agreements:
        installments: List[Installment] = list(agreement.installments.all())
        installments_data = []

        for installment in installments:
            # Preciso verificar se a parcela tem boleto associado
            if not hasattr(installment, 'boleto') or not installment.boleto:
                continue
            

            boleto: Boleto = installment.boleto
            installments_data.append({
                "number": installment.number,
                "due_date": installment.due_date,
                "boleto": boleto.dict(dry=True) if boleto else None,
            })

        output_data.append({
            "number": agreement.number,
            "creditor": agreement.creditor.dict(),
            "installments": installments_data
        })

    return ReturnSchema(code=200, data=output_data)


@agreement_router.get('/number/{str:agreement_number}', response={200: ReturnSchema[AgreementOutSchema]}, auth=AllowHumansAuth())
@endpoint(None)
def get_agreement_by_number(request: CustomRequest, agreement_number: str):
    lgr.info(f"Ator {request.actor.identification} (ID: {request.actor.id}) está acessando o acordo pelo número {agreement_number}")
    agreement: Agreement = AgreementController.get(number=agreement_number)
    if request.actor.is_human and agreement.payer.user.id != request.actor.id:
        raise HttpFriendlyException(403, "Você não tem permissão para acessar esse acordo")

    return ReturnSchema(code=200, data=agreement)
