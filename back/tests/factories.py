from datetime import timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from factory.django import DjangoModelFactory
from faker import Faker
import factory

from app.models import Agreement, ApiConsumer, Boleto, Creditor, Installment, LoginCode, Payer, User

fake = Faker()


class TimestampedModelFactory(DjangoModelFactory):
    created_at = factory.Faker('date_time_this_decade', tzinfo=ZoneInfo('UTC'))
    updated_at = factory.Faker('date_time_this_decade', tzinfo=ZoneInfo('UTC'))


class UserFactory(TimestampedModelFactory):
    class Meta:
        model = User

    password = factory.Faker('password')
    cpf = factory.Faker('numerify', text='###########')


class PayerFactory(TimestampedModelFactory):
    class Meta:
        model = Payer
    
    name = factory.Faker('name')
    phone = factory.Faker('numerify', text='###########')
    user = factory.SubFactory(UserFactory)


class CreditorFactory(TimestampedModelFactory):
    class Meta:
        model = Creditor
    
    name = factory.Faker('name')
    reissue_margin = fake.pyint(min_value=0, max_value=10)


class AgreementFactory(TimestampedModelFactory):
    class Meta:
        model = Agreement
    
    number = factory.LazyFunction(lambda: fake.pyint(min_value=1, max_value=1000))
    payer = factory.SubFactory(PayerFactory)
    creditor = factory.SubFactory(CreditorFactory)


class InstallmentFactory(TimestampedModelFactory):
    class Meta:
        model = Installment
    
    number = factory.LazyFunction(lambda: fake.pyint(min_value=1, max_value=1000))
    agreement = factory.SubFactory(AgreementFactory)
    due_date = factory.Faker('future_date')



class BoletoFactory(TimestampedModelFactory):
    class Meta:
        model = Boleto
    
    installment = factory.SubFactory(InstallmentFactory)
    status = factory.Iterator([status.value for status in Boleto.Status])
    @factory.lazy_attribute
    def pdf(self):
        return SimpleUploadedFile(
            f"boleto_{fake.uuid4()}.pdf", 
            b"Fake PDF Content", 
            content_type="application/pdf")


class ApiConsumerFactory(TimestampedModelFactory):
    class Meta:
        model = ApiConsumer
    
    name = factory.Faker('company')


class LoginCodeFactory(TimestampedModelFactory):
    class Meta:
        model = LoginCode

    code = factory.Faker('numerify', text='######')
    user = factory.SubFactory(UserFactory)
    expiration_date = factory.LazyFunction(lambda: timezone.now() + timedelta(minutes=settings.SMS_EXPIRATION))
    used = False
