import logging

from django.core.handlers.wsgi import WSGIRequest
from ninja import Query, Router
from ninja.responses import codes_4xx

from app.api import endpoint
from app.controllers.installment_controller import InstallmentController
from app.models import Installment
from app.schemas import DeleteSchema, ErrorSchema, ListSchema, PaginatedOutSchema
from app.schemas.installment_schemas import InstallmentInSchema, InstallmentOutSchema, InstallmentPatchInSchema


installment_router = Router()
lgr = logging.getLogger(__name__)


@installment_router.post('/', response={201: InstallmentOutSchema, codes_4xx: ErrorSchema})
@endpoint
def create_installment(request: WSGIRequest, data: InstallmentInSchema):
    new_installment: Installment = InstallmentController.create(data)
    return new_installment, 201


@installment_router.get('/{int:installment_id}', response={200: InstallmentOutSchema})
@endpoint
def view_installment(request: WSGIRequest, installment_id: int):
    installment: Installment = InstallmentController.get(id=installment_id)
    return installment, 200


@installment_router.patch('/{int:installment_id}', response={200: InstallmentOutSchema})
@endpoint
def edit_installment(request: WSGIRequest, installment_id: int, data: InstallmentPatchInSchema):
    installment: Installment = InstallmentController.update(installment_id, data)
    return installment, 200


@installment_router.get('/', response={200: PaginatedOutSchema})
@endpoint
def list_installment(request: WSGIRequest, data: Query[ListSchema]):
    installments_page, paginator = InstallmentController.filter(data)
    return {
        "page": installments_page,
        "paginator": paginator,
    }, 200


@installment_router.delete('/{int:installment_id}', response={200: DeleteSchema})
@endpoint
def delete_installment(request: WSGIRequest, installment_id: int):
    InstallmentController.delete(id=installment_id)
    return {"message": "Parcela deletada!"}, 200
