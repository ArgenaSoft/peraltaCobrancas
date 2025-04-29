from zoneinfo import ZoneInfo

from app.models import Payer, User
import factory
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker()


class TimestampedModelFactory(DjangoModelFactory):
    created_at = factory.Faker('date_time_this_decade', tzinfo=ZoneInfo('UTC'))
    updated_at = factory.Faker('date_time_this_decade', tzinfo=ZoneInfo('UTC'))

class UserFactory(TimestampedModelFactory):
    class Meta:
        model = User

    password = factory.Faker('password')
    cpf = factory.Faker('numerify', text='###.###.###-##')

class PayerFactory(TimestampedModelFactory):
    class Meta:
        model = Payer
    
    name = factory.Faker('name')
    phone = factory.Faker('phone_number')
    user = factory.SubFactory(UserFactory)
