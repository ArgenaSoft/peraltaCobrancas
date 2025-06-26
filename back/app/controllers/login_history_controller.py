import logging

from app.controllers import BaseController
from app.models import LoginHistory
from app.repositories.login_history_repository import LoginHistoryRepository

lgr =  logging.getLogger(__name__)


class LoginHistoryController(BaseController[LoginHistoryRepository, LoginHistory]):
    REPOSITORY = LoginHistoryRepository
    MODEL = LoginHistory
