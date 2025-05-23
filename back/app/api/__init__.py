from functools import wraps
import logging
from typing import Any, Optional, Tuple, Union

from ninja import Router
from ninja.responses import codes_3xx, codes_4xx, codes_5xx

from app.exceptions import HttpFriendlyException
from app.schemas import ReturnSchema
from config import DEV, ENV

lgr = logging.getLogger(__name__)


def endpoint(func):
    @wraps(func)
    def wrapper(*args, **kwargs) -> tuple:
        try:
            response: ReturnSchema = func(*args, **kwargs)
        except HttpFriendlyException as e:
            response = ReturnSchema.from_http_friendly_exception(e)
        except Exception as e:
            lgr.exception(e)
            if ENV == DEV:
                raise

            response = ReturnSchema(message="Internal Server Error", code=500)

        return response.code, response.model_dump()
    
    return wrapper


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
        self.add_missing_codes(response_schemas, codes_4xx, ReturnSchema)
        self.add_missing_codes(response_schemas, codes_5xx, ReturnSchema)

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
