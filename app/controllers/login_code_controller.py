from datetime import datetime, timedelta
import logging

from faker import Faker

from app.models import User
from app.repositories.login_code_repository import LoginCodeRepository

lgr = logging.getLogger(__name__)

fake = Faker()

class LoginCodeController:
    @classmethod
    def create(cls, user: User):
        code = 'PC' + fake.lexify('?????')
        expiration = datetime.now() + timedelta(minutes=5)

        data = {
            'code': code, 
            'user': user,
            'expiration_date': expiration
        }
        login_code = LoginCodeRepository.create(data)
        return login_code
