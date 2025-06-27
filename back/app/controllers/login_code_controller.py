from datetime import timedelta
import logging
from typing import Optional

from django.conf import settings
from faker import Faker
from django.utils import timezone

from app.exceptions import ShouldWaitToGenerateAnotherCode
from app.models import LoginCode, User
from app.repositories.login_code_repository import LoginCodeRepository

lgr = logging.getLogger(__name__)

fake = Faker()

class LoginCodeController:
    @classmethod
    def create(cls, user: User) -> LoginCode:
        code = cls.get_user_active_code(user)
        if code:
            wait_time = code.expiration_date - timezone.now()
            raise ShouldWaitToGenerateAnotherCode(wait_time)

        code = 'PC' + fake.lexify('?????')
        expiration = timezone.now() + timedelta(seconds=settings.SMS_EXPIRATION)

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
