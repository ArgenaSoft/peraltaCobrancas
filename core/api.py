import logging
from ninja import NinjaAPI
from ninja.responses import Response

from app.api.payer_api import payer_router
from app.exceptions import HttpFriendlyException

lgr = logging.getLogger(__name__)

api = NinjaAPI()

@api.exception_handler(HttpFriendlyException)
def handle_friendly_exceptions(request, exc: HttpFriendlyException):
    return Response({"message": exc.message}, status=exc.status_code)

api.add_router('/payer', payer_router)