import re
from typing import Dict

from django.core.handlers.wsgi import WSGIRequest
from ninja import Query
from ninja.responses import codes_4xx

from app.api import CustomRouter, endpoint
from app.controllers.login_code_controller import LoginCodeController
from app.controllers.user_controller import UserController
from app.models import LoginCode
from app.schemas import ErrorSchema
from app.schemas.user_schemas import UserGetCodeSchema


user_router = CustomRouter()


@user_router.get('/get_code', response={201: Dict, codes_4xx: ErrorSchema}, auth=None)
@endpoint
def get_code(request: WSGIRequest, data: Query[UserGetCodeSchema]):
    """
    Gera um codigo de login a ser enviado via sms
    """
    filters = {
        "cpf": re.sub(r"\D", "", data.cpf),
        "payer__phone": re.sub(r"\D", "", data.phone),
    }
    print(filters)
    user = UserController.get(**filters)
    code: LoginCode = LoginCodeController.create(user)

    print(code.code)
    return {"code": code.code}, 201
