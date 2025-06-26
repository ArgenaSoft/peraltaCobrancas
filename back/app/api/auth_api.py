import logging
import re

from django.core.handlers.wsgi import WSGIRequest

from app.api import CustomRouter
from app.controllers.auth_controller import AuthController
from app.schemas import ReturnSchema
from app.schemas.auth_schemas import LoginSchema, RefreshInputSchema, RefreshPairSchema, TokenOutSchema

lgr = logging.getLogger(__name__)

auth_router = CustomRouter(tags=["Autenticação"])


@auth_router.post("/token", response={200: ReturnSchema[TokenOutSchema]}, auth=None)
def login(request: WSGIRequest, data: LoginSchema):
    data.cpf = re.sub(r"\D", "", data.cpf)
    data.phone = re.sub(r"\D", "", data.phone)

    token, payer_name = AuthController.login(data)
    return_data = {
        "access": str(token.access_token),
        "refresh": str(token),
        "username": payer_name
    }

    return ReturnSchema(code=200, data=return_data)


@auth_router.post("/refresh", response={200: ReturnSchema[RefreshPairSchema]}, auth=None)
def refresh_token_pair(request: WSGIRequest, data: RefreshInputSchema):
    return ReturnSchema(code=200, data=AuthController.refresh_pair(data))
