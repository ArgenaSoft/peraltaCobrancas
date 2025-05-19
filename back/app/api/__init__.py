from functools import wraps
import logging
from typing import Any

from ninja import Router
from ninja.responses import codes_3xx, codes_4xx, codes_5xx

from app.exceptions import HttpFriendlyException
from app.schemas import ErrorSchema
from config import DEV, ENV

lgr = logging.getLogger(__name__)


def endpoint(func):
    @wraps(func)
    def wrapper(*args, **kwargs) -> tuple:
        response = {}

        try:
            data, code = func(*args, **kwargs)
        except HttpFriendlyException as e:
            code = e.status_code
            data = ErrorSchema(message=e.message, code=e.status_code, data=e.data)
        except Exception as e:
            lgr.exception(e)
            if ENV == DEV:
                raise
            code = 500
            data = ErrorSchema(message="Internal Server Error", code=code)
            
        return code, data
    
    return wrapper


class CustomRouter(Router):
    """
        Não queria setar manualmente em todas as rotas o mesmo esquema de 
        resposta para os códigos de erro
    """

    def add_missing_codes(self, response_schemas: dict, code_set: frozenset, schema: Any):
        existing_codes = set(response_schemas.keys())
        missing = code_set - existing_codes
        response_schemas[missing] = schema

    def create_missing_response(self, response_schemas: dict):
        self.add_missing_codes(response_schemas, codes_4xx, ErrorSchema)
        self.add_missing_codes(response_schemas, codes_5xx, ErrorSchema)

        return response_schemas

    def get(self, *args, **kwargs):
        kwargs['response'] = self.create_missing_response(
            kwargs.get('response', {})
        )

        return super().get(*args, **kwargs)