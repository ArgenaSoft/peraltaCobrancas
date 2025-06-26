import re
from typing import Dict

from django.core.handlers.wsgi import WSGIRequest
from ninja import Query
from ninja.responses import codes_4xx

from app.api import CustomRouter, endpoint
from app.controllers.login_code_controller import LoginCodeController
from app.controllers.user_controller import UserController
from app.exceptions import ShouldWaitToGenerateAnotherCode
from app.models import LoginCode, User
from app.schemas import ReturnSchema
from app.schemas.user_schemas import UserGetCodeSchema, UserWaitToGetCodeSchema
from app.sms_api import send_sms
from config import DEV, ENV


user_router = CustomRouter()


@user_router.get('/get_code', response={201: ReturnSchema, 400: ReturnSchema[UserWaitToGetCodeSchema]}, auth=None)
@endpoint
def get_code(request: WSGIRequest, data: Query[UserGetCodeSchema]):
    """
    Gera um codigo de login a ser enviado via sms
    """
    filters = {
        "cpf": re.sub(r"\D", "", data.cpf),
    }

    user: User = UserController.get(**filters)
    try:
        code: LoginCode = LoginCodeController.create(user)
    except ShouldWaitToGenerateAnotherCode as e:
        return ReturnSchema(
            code=400, 
            message=e.message, 
            data={"wait_time_seconds": e.data["wait_time_seconds"]})

    return_data = {}
    send_sms(data.phone, f"Seu codigo de acesso para a plataforma Peralta Cobranças: {code.code}.")
    if ENV == DEV:
        print(f"Generated code: {code.code}")
        return_data = {"code": code.code}

    return ReturnSchema(code=201, data=return_data)
