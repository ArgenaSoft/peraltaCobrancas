import logging
import os

from ninja import NinjaAPI
from ninja.responses import Response

from app.api.payer_api import payer_router
from app.api.user_api import user_router
from app.api.auth_api import auth_router
from app.exceptions import HttpFriendlyException
from core.auth import CustomJWTAuth

lgr = logging.getLogger(__name__)

# Isso aqui permite que a verdadeira causa de alguns problemas apareça e não
# seja mascarada por um erro padrão do ninja
os.environ["NINJA_SKIP_REGISTRY"] = "yes"

api = NinjaAPI()

@api.exception_handler(HttpFriendlyException)
def handle_friendly_exceptions(request, exc: HttpFriendlyException):
    return Response({"message": exc.message}, status=exc.status_code)

api.add_router('/payer', payer_router, auth=CustomJWTAuth())
api.add_router('/user', user_router)
api.add_router('/auth', auth_router)
