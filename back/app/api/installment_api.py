import logging
from typing import Dict

from ninja import Query
from ninja.responses import codes_4xx

from app.api import CustomRouter, endpoint
from app.controllers.installment_controller import InstallmentController
from app.exceptions import HttpFriendlyException
from app.models import Installment
from app.schemas import DeleteSchema, ReturnSchema, ListSchema, PaginatedOutSchema
from app.schemas.installment_schemas import InstallmentInSchema, InstallmentOutSchema, InstallmentPatchInSchema
from core.auth import AllowHumansAuth
from core.custom_request import CustomRequest


installment_router = CustomRouter()
lgr = logging.getLogger(__name__)


@installment_router.post('/', response={201: ReturnSchema[InstallmentOutSchema]})
@endpoint
def create_installment(request: CustomRequest, data: InstallmentInSchema):
    new_installment: Installment = InstallmentController.create(data)
    return ReturnSchema(code=201, data=new_installment)


@installment_router.get('/{int:installment_id}', response={200: ReturnSchema[InstallmentOutSchema]})
@endpoint
def view_installment(request: CustomRequest, installment_id: int):
    installment: Installment = InstallmentController.get(id=installment_id)

    if request.actor.is_human and installment.agreement.payer.user.id != request.actor.id:
        raise HttpFriendlyException(403, "Você não tem permissão para acessar essa parcela")

    return ReturnSchema(code=200, data=installment)


@installment_router.patch('/{int:installment_id}', response={200: ReturnSchema[InstallmentOutSchema]})
@endpoint
def edit_installment(request: CustomRequest, installment_id: int, data: InstallmentPatchInSchema):
    installment: Installment = InstallmentController.update(installment_id, data)
    return ReturnSchema(code=200, data=installment)


@installment_router.get('/', response={200: ReturnSchema[PaginatedOutSchema[InstallmentOutSchema]]}, auth=AllowHumansAuth())
@endpoint
def list_installment(request: CustomRequest, data: Query[ListSchema]):
    data.build_filters_from_query(request.GET.dict())

    if request.actor.is_human:
        data.filters['agreement__payer__user_id'] = request.actor.id

    installments_page, paginator = InstallmentController.filter_paginated(data)
    return ReturnSchema(
        code=200,
        data=PaginatedOutSchema.build(installments_page, paginator)
    )


@installment_router.delete('/{int:installment_id}', response={200: ReturnSchema})
@endpoint
def delete_installment(request: CustomRequest, installment_id: int):
    InstallmentController.delete(id=installment_id)
    return ReturnSchema(code=200)
