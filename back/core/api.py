import logging
import os

from ninja import NinjaAPI
from ninja.responses import Response

from app.api.payer_api import payer_router
from app.api.user_api import user_router
from app.api.auth_api import auth_router
from app.api.creditor_api import creditor_router
from app.api.agreement_api import agreement_router
from app.api.installment_api import installment_router
from app.api.boleto_api import boleto_router
from app.exceptions import HttpFriendlyException
from config import DEV, ENV
from core.auth import CustomJWTAuth


lgr = logging.getLogger(__name__)
# Isso aqui permite que a verdadeira causa de alguns problemas apareça e não
# seja mascarada por um erro padrão do ninja
os.environ["NINJA_SKIP_REGISTRY"] = "yes"


api = NinjaAPI()


@api.exception_handler(HttpFriendlyException)
def handle_friendly_exceptions(request, exc: HttpFriendlyException):
    return Response(exc.dict(), status=exc.status_code)


@api.exception_handler(Exception)
def handle_wild_exceptions(request, exc: HttpFriendlyException):
    if ENV == DEV:
        return Response({"error": str(exc)}, status=500)
    else:
        return Response({"error": "Internal Server Error"}, status=500)


api.add_router('/payer', payer_router, auth=CustomJWTAuth())
api.add_router('/user', user_router)
api.add_router('/auth', auth_router)
api.add_router('/creditor', creditor_router, auth=CustomJWTAuth())
api.add_router('/agreement', agreement_router, auth=CustomJWTAuth())
api.add_router('/installment', installment_router, auth=CustomJWTAuth())
api.add_router('/boleto', boleto_router, auth=CustomJWTAuth())
