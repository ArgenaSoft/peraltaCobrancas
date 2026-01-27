from functools import wraps
import logging
from traceback import format_exc
from typing import Any, Union

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
                    raise e
                response = ReturnSchema(message="Erro interno.", code=500)

            teste = response.code, response
            print(response.code)
            print(response.model_dump())
            print('---------------')
            return teste

        return wrapper
    return decorator


class CustomRouter(Router):
    """
        Não queria setar manualmente em todas as rotas o mesmo esquema de 
        resposta para os códigos de erro
    """

    def add_missing_codes(self, response_schemas: Union[dict, Any], code_set: frozenset, schema: Any):
        if not isinstance(response_schemas, dict):
            raise TypeError("O dicionário de retornos para as rotas precisa ser um dicionário. Exemplo: 'response={200: ReturnSchema}'")

        existing_codes = set(response_schemas.keys())
        missing = code_set - existing_codes
        response_schemas[missing] = schema

    def create_missing_response(self, response_schemas: dict):
        self.add_missing_codes(response_schemas, frozenset([400, 404, 500]), ReturnSchema)

        return response_schemas

    def get(self, *args, **kwargs):
        kwargs['response'] = self.create_missing_response(
            kwargs.get('response', {})
        )

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs['response'] = self.create_missing_response(
            kwargs.get('response', {})
        )

        return super().post(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        kwargs['response'] = self.create_missing_response(
            kwargs.get('response', {})
        )

        return super().delete(*args, **kwargs)

    def patch(self, *args, **kwargs):
        kwargs['response'] = self.create_missing_response(
            kwargs.get('response', {})
        )

        return super().patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        kwargs['response'] = self.create_missing_response(
            kwargs.get('response', {})
        )

        return super().put(*args, **kwargs)

