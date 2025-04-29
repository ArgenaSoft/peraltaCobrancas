from typing import Dict
from django.core.handlers.wsgi import WSGIRequest
from ninja import Query, Router

from app.api import endpoint
from app.controllers.login_code_controller import LoginCodeController
from app.controllers.user_controller import UserController
from app.models import LoginCode
from app.schemas import UserSchema


user_router = Router()


@user_router.get('/get_code', response={201: Dict})
@endpoint
def get_code(request: WSGIRequest, data: Query[UserSchema.GetCode]):
    """
    Gera um codigo de login a ser enviado via sms
    """
    filters = {
        "cpf": data.cpf,
        "payer__phone": data.phone,
    }

    user = UserController.get(**filters)
    code: LoginCode = LoginCodeController.create(user)

    return {"code": code.code}, 201
