from functools import wraps
import logging

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
