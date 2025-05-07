from datetime import timedelta
import logging
from typing import Optional

from faker import Faker
from django.utils import timezone

from app.exceptions import HttpFriendlyException
from app.models import LoginCode, User
from app.repositories.login_code_repository import LoginCodeRepository
from app.utils import beautify_timedelta
from config import SMS_CODE_EXPIRATION_SECONDS

lgr = logging.getLogger(__name__)

fake = Faker()

class LoginCodeController:
    @classmethod
    def create(cls, user: User) -> LoginCode:
        code = cls.get_user_active_code(user)
        if code:
            wait_time = code.expiration_date - timezone.now()
            raise HttpFriendlyException(
                400,
                f"Aguarde {beautify_timedelta(wait_time)} para gerar um novo código",
                {"wait_time_seconds": wait_time.total_seconds()}
            )

        code = 'PC' + fake.lexify('?????')
        expiration = timezone.now() + timedelta(seconds=SMS_CODE_EXPIRATION_SECONDS)

        data = {
            'code': code, 
            'user': user,
            'expiration_date': expiration
        }
        login_code = LoginCodeRepository.create(data)
        return login_code

    @classmethod
    def get_user_active_code(cls, user: User) -> Optional[LoginCode]:
        try:
            return LoginCodeRepository.get(
                friendly=False,
                user=user,
                expiration_date__gt=timezone.now()
            )
        except LoginCode.DoesNotExist:
            return None
