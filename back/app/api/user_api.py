import logging
import re

from django.core.handlers.wsgi import WSGIRequest
from ninja import Query

from app.api import CustomRouter, endpoint
from app.controllers.login_code_controller import LoginCodeController
from app.controllers.user_controller import UserController
from app.exceptions import ShouldWaitToGenerateAnotherCode
from app.models import LoginCode, User
from app.schemas import ReturnSchema
from app.schemas.user_schemas import UserGetCodeSchema, UserWaitToGetCodeSchema
from app.sms_api import send_sms
from config import DEV, ENV


lgr = logging.getLogger(__name__)
user_router = CustomRouter(tags=["Usuários"])


@user_router.get('/get_code', response={201: ReturnSchema, 400: ReturnSchema[UserWaitToGetCodeSchema], 404: ReturnSchema}, auth=None)
@endpoint(None)
def get_code(request: WSGIRequest, data: Query[UserGetCodeSchema]):
    """
    Gera um codigo de login a ser enviado via sms
    """
    lgr.info(f"Usuário {data.cpf_cnpj} solicitou um código de acesso")
    filters = {
        "cpf_cnpj": re.sub(r"\D", "", data.cpf_cnpj),
    }

    user: User = UserController.get(**filters)
    try:
        code: LoginCode = LoginCodeController.create(user)
        lgr.info(f"Código gerado para o usuário {user.identification}: {code.code}")
    except ShouldWaitToGenerateAnotherCode as e:
        lgr.warning(f"Usuário {user.identification} tentou gerar um código antes do tempo de espera: {e.message}")
        return ReturnSchema(
            code=400, 
            message=e.message, 
            data={"wait_time_seconds": e.data["wait_time_seconds"]})

    return_data = {}
    sent = send_sms(data.phone, f"Seu codigo de acesso para a plataforma Peralta Cobranças: {code.code}.")
    if not sent:
        return ReturnSchema(code=500, message="Não foi possível enviar o SMS. Peça o código para o suporte.")

    if ENV == DEV:
        print(f"Generated code: {code.code}")
        return_data = {"code": code.code}

    return ReturnSchema(code=201, data=return_data)
