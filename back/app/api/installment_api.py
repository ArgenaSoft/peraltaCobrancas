import logging

from ninja import Query
from ninja.responses import codes_4xx

from app.api import CustomRouter, endpoint
from app.controllers.installment_controller import InstallmentController
from app.exceptions import HttpFriendlyException
from app.models import Installment
from app.schemas import DeleteSchema, ErrorSchema, ListSchema, PaginatedOutSchema
from app.schemas.installment_schemas import InstallmentInSchema, InstallmentOutSchema, InstallmentPatchInSchema
from core.auth import AllowHumansAuth
from core.custom_request import CustomRequest


installment_router = CustomRouter()
lgr = logging.getLogger(__name__)


@installment_router.post('/', response={201: InstallmentOutSchema, codes_4xx: ErrorSchema})
@endpoint
def create_installment(request: CustomRequest, data: InstallmentInSchema):
    new_installment: Installment = InstallmentController.create(data)
    return new_installment, 201


@installment_router.get('/{int:installment_id}', response={200: InstallmentOutSchema})
@endpoint
def view_installment(request: CustomRequest, installment_id: int):
    installment: Installment = InstallmentController.get(id=installment_id)

    if request.actor.is_human and installment.agreement.payer.user.id != request.actor.id:
        raise HttpFriendlyException(403, "Você não tem permissão para acessar essa parcela")

    return installment, 200


@installment_router.patch('/{int:installment_id}', response={200: InstallmentOutSchema})
@endpoint
def edit_installment(request: CustomRequest, installment_id: int, data: InstallmentPatchInSchema):
    installment: Installment = InstallmentController.update(installment_id, data)
    return installment, 200


@installment_router.get('/', response={200: PaginatedOutSchema}, auth=AllowHumansAuth())
@endpoint
def list_installment(request: CustomRequest, data: Query[ListSchema]):
    if request.actor.is_human:
        filters = {
            'agreement__payer__user_id': request.actor.id,
        }
        data.filters.update(filters)

    installments_page, paginator = InstallmentController.filter(data)
    return PaginatedOutSchema.build(installments_page, paginator), 200



@installment_router.delete('/{int:installment_id}', response={200: DeleteSchema})
@endpoint
def delete_installment(request: CustomRequest, installment_id: int):
    InstallmentController.delete(id=installment_id)
    return {"message": "Parcela deletada!"}, 200
