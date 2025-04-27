import logging
import os
from ninja import NinjaAPI
from ninja.responses import Response

from app.api.payer_api import payer_router
from app.exceptions import HttpFriendlyException

lgr = logging.getLogger(__name__)

# Isso aqui permite que a verdadeira causa de alguns problemas apareça e não
# seja mascarada por um erro padrão do ninja
os.environ["NINJA_SKIP_REGISTRY"] = "yes"

api = NinjaAPI()

@api.exception_handler(HttpFriendlyException)
def handle_friendly_exceptions(request, exc: HttpFriendlyException):
    return Response({"message": exc.message}, status=exc.status_code)

api.add_router('/payer', payer_router)