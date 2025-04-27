from functools import wraps
import logging

from app.exceptions import HttpFriendlyException


lgr = logging.getLogger(__name__)


def endpoint(func):
    @wraps(func)
    def wrapper(*args, **kwargs) -> tuple:
        response = {}

        try:
            data, code = func(*args, **kwargs)
            response['data'] = data
            response['code'] = code
        except HttpFriendlyException as e:
            response['code'] = e.status_code
            response['data'] = {'message': e.message}
        except Exception as e:
            lgr.error(f"Error in endpoint: {e}")
            raise
            
        return response['code'], response['data']
    
    return wrapper
