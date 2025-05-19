import logging

from ninja import Query
from ninja.responses import codes_4xx

from app.api import CustomRouter, endpoint
from app.controllers.agreement_controller import AgreementController
from app.exceptions import HttpFriendlyException
from app.models import Agreement
from app.schemas import DeleteSchema, ErrorSchema, ListSchema, PaginatedOutSchema
from app.schemas.agreement_schemas import AgreementInSchema, AgreementOutSchema, AgreementPatchInSchema
from core.auth import AllowHumansAuth
from core.custom_request import CustomRequest

agreement_router = CustomRouter()
lgr = logging.getLogger(__name__)


@agreement_router.post('/', response={201: AgreementOutSchema, codes_4xx: ErrorSchema})
@endpoint
def create_agreement(request: CustomRequest, data: AgreementInSchema):
    new_agreement: Agreement = AgreementController.create(data)
    return new_agreement, 201


@agreement_router.get('/{int:agreement_id}', response={200: AgreementOutSchema})
@endpoint
def view_agreement(request: CustomRequest, agreement_id: int):
    agreement: Agreement = AgreementController.get(id=agreement_id)
    if request.actor.is_human and agreement.payer.user.id != request.actor.id:
        raise HttpFriendlyException(403, "Você não tem permissão para acessar esse acordo")

    return agreement, 200


@agreement_router.patch('/{int:agreement_id}', response={200: AgreementOutSchema})
@endpoint
def edit_agreement(request: CustomRequest, agreement_id: int, schema: AgreementPatchInSchema):
    agreement: Agreement = AgreementController.update(agreement_id, schema)
    return agreement, 200


@agreement_router.get('/', response={200: PaginatedOutSchema}, auth=AllowHumansAuth())
@endpoint
def list_agreement(request: CustomRequest, data: Query[ListSchema]):
    if request.actor.is_human:
        filters = {
            'payer__user_id': request.actor.id,
        }
        data.filters.update(filters)

    agreements_page, paginator = AgreementController.filter(data)
    return PaginatedOutSchema.build(agreements_page, paginator), 200


@agreement_router.delete('/{int:agreement_id}', response={200: DeleteSchema})
@endpoint
def delete_payer(request: CustomRequest, agreement_id: int):
    AgreementController.delete(id=agreement_id)
    return {"message": "Acordo deletado!"}, 200
