
from datetime import timedelta
from typing import Dict, Optional

from app.utils import beautify_timedelta


class HttpFriendlyException(Exception):
    def __init__(self, code: int, message: str, data: Optional[Dict] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


    def dict(self) -> Dict:
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }


class ShouldWaitToGenerateAnotherCode(HttpFriendlyException):
    data: Dict

    def __init__(self, wait_time: timedelta):
        super().__init__(
            400,
            f"Aguarde {beautify_timedelta(wait_time)} para gerar um novo código",
            {"wait_time_seconds": wait_time.total_seconds()}
        )


class InvalidCsvDelimiterException(HttpFriendlyException):
    def __init__(self, message: str = "Delimitador CSV inválido. Use vírgula (,) ou ponto e vírgula (;) como delimitador."):
        super().__init__(400, message)
