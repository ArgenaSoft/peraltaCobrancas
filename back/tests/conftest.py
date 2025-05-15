import pytest

from app.controllers.auth_controller import AuthController
from app.models import Agreement, ApiConsumer, Creditor, Installment, LoginCode, Payer
from tests.factories import AgreementFactory, ApiConsumerFactory, CreditorFactory, InstallmentFactory, LoginCodeFactory, PayerFactory, UserFactory


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests by default.
    """
    pass


@pytest.fixture
def user_client(client):
    user = UserFactory.create()
    token = AuthController.get_token(user.id, "user")
    
    client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token.access_token}'
    
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
    yield payer
    payer.delete()
    assert not Payer.objects.filter(pk=payer.pk).exists(), "Teardown failed: Payer was not removed from the database."


@pytest.fixture
def payer_generator():
    created_payers = []

    def _create_payers(n):
        payers = PayerFactory.create_batch(n)
        created_payers.extend(payers)
        return payers

    yield _create_payers

    # Teardown
    for payer in created_payers:
        payer.delete()

    assert not Payer.objects.filter(pk__in=[payer.pk for payer in created_payers]).exists(), "Teardown failed: Payers were not removed from the database."


@pytest.fixture
def login_code():
    code = LoginCodeFactory.create()
    yield code
    code.delete()
    assert not LoginCode.objects.filter(pk=code.pk).exists(), "Teardown failed: LoginCode was not removed from the database."


@pytest.fixture
def creditor():
    creditor = CreditorFactory.create()
    yield creditor
    creditor.delete()
    assert not Creditor.objects.filter(pk=creditor.pk).exists(), "Teardown failed: Creditor was not removed from the database."

@pytest.fixture
def agreement():
    agreement = AgreementFactory.create()
    yield agreement
    agreement.delete()
    assert not Agreement.objects.filter(pk=agreement.pk).exists(), "Teardown failed: Agreement was not removed from the database."

@pytest.fixture
def installment():
    installment = InstallmentFactory.create()
    yield installment
    installment.delete()
    assert not Installment.objects.filter(pk=installment.pk).exists(), "Teardown failed: Installment was not removed from the database."
