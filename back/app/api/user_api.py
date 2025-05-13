from typing import Dict

from django.core.handlers.wsgi import WSGIRequest
from ninja import Query, Router
from ninja.responses import codes_4xx

from app.api import endpoint
from app.controllers.login_code_controller import LoginCodeController
from app.controllers.user_controller import UserController
from app.models import LoginCode
from app.schemas import ErrorSchema
from app.schemas.user_schemas import UserGetCodeSchema


user_router = Router()


@user_router.get('/get_code', response={201: Dict, codes_4xx: ErrorSchema})
@endpoint
def get_code(request: WSGIRequest, data: Query[UserGetCodeSchema]):
    """
    Gera um codigo de login a ser enviado via sms
    """
    filters = {
        "cpf": data.cpf,
        "payer__phone": data.phone,
    }

    user = UserController.get(**filters)
    code: LoginCode = LoginCodeController.create(user)
    
    print(code.code)
    return {"code": code.code}, 201
