from functools import wraps
import logging

from app.exceptions import HttpFriendlyException
from app.schemas import ErrorSchema


lgr = logging.getLogger(__name__)


def endpoint(func):
    @wraps(func)
    def wrapper(*args, **kwargs) -> tuple:
        response = {}

        try:
            data, code = func(*args, **kwargs)
            response['code'] = code
        except HttpFriendlyException as e:
            response['code'] = e.status_code
            data = ErrorSchema(message=e.message, code=e.status_code, data=e.data)
        except Exception as e:
            lgr.error(f"Error in endpoint: {e}")
            raise
            
        return response['code'], data
    
    return wrapper
