
from typing import Dict


class HttpFriendlyException(Exception):
    def __init__(self, status_code: int, message: str, data: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.data = data

