import logging

from ninja import Query

from app.api import CustomRouter, endpoint
from app.controllers.login_history_controller import LoginHistoryController
from app.schemas import ReturnSchema, ListSchema, PaginatedOutSchema
from app.schemas.login_history_schemas import LoginHistoryOutSchema
from core.custom_request import CustomRequest


login_history_router = CustomRouter(tags=["Histórico de Login"])
lgr = logging.getLogger(__name__)


@login_history_router.get('/', response={200: ReturnSchema[PaginatedOutSchema[LoginHistoryOutSchema]]})
@endpoint
def list_login_history(request: CustomRequest, data: Query[ListSchema]):
    data.build_filters_from_query(request.GET.dict())
    login_histories_page, paginator = LoginHistoryController.filter_paginated(data)
    return ReturnSchema(
        code=200, 
        data=PaginatedOutSchema.build(login_histories_page, paginator)
    )
