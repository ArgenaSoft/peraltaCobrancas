import pytest

from app.controllers.auth_controller import AuthController
from app.models import Agreement, ApiConsumer, Boleto, Creditor, Installment, LoginCode, Payer, User
from tests.factories import AgreementFactory, ApiConsumerFactory, BoletoFactory, CreditorFactory, InstallmentFactory, LoginCodeFactory, PayerFactory, UserFactory
from tests.utils import login_client_as


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests by default.
    """
    pass


@pytest.fixture
def user_client(client):
    user = UserFactory.create()
    client = login_client_as(client, user)
    return client


@pytest.fixture
def system_client(client):
    system: ApiConsumer = ApiConsumerFactory.create()
    token = AuthController.get_token(system.api_key, "system")
    
    client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token.access_token}'
    
    return client


@pytest.fixture
def payer():
    payer = PayerFactory.create()
    return payer


@pytest.fixture
def payer_generator():
    created_payers = []

    def _create_payers(n):
        payers = PayerFactory.create_batch(n)
        created_payers.extend(payers)
        return payers

    return _create_payers

@pytest.fixture
def login_code():
    code = LoginCodeFactory.create()
    return code


@pytest.fixture
def user():
    user = UserFactory.create()
    return user


@pytest.fixture
def creditor():
    creditor = CreditorFactory.create()
    return creditor

@pytest.fixture
def agreement():
    agreement = AgreementFactory.create()
    return agreement

@pytest.fixture
def installment():
    installment = InstallmentFactory.create()
    return installment

@pytest.fixture
def boleto():
    boleto = BoletoFactory.create()
    return boleto
