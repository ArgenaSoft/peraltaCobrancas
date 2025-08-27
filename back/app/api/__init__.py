from functools import wraps
import logging
from traceback import format_exc

from ninja import Router

from app.exceptions import HttpFriendlyException
from app.schemas import ReturnSchema
from config import DEV, ENV
from core.custom_request import CustomRequest

lgr = logging.getLogger(__name__)


def endpoint(log_action: str | None = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request: CustomRequest = kwargs.get("request") or args[0]

            if log_action:
                try:
                    lgr.info(f"Ator {request.actor.identification} (ID: {request.actor.id}) -> {log_action}")
                except Exception:
                    pass  # Failsafe no log, caso `request.actor` não esteja disponível

            try:
                response: ReturnSchema = func(*args, **kwargs)
            except HttpFriendlyException as e:
                lgr.debug(f"HttpFriendlyException capturada: {e.code} - {e.message}")
                response = ReturnSchema.from_http_friendly_exception(e)
            except Exception as e:
                lgr.exception(e)
                lgr.error(format_exc())
                if ENV == DEV:
                    raise
                response = ReturnSchema(message="Erro interno.", code=500)

            return response.code, response.model_dump()

        return wrapper
    return decorator


class CustomRouter(Router):
    pass
