from django.test import Client
import pytest
import os
import glob
import shutil
from django.conf import settings
from unittest.mock import patch

from app.controllers.auth_controller import AuthController
from app.models import ApiConsumer
from tests.factories import AgreementFactory, ApiConsumerFactory, BoletoFactory, CreditorFactory, InstallmentFactory, LoginCodeFactory, LoginHistoryFactory, PayerFactory, UserFactory
from tests.utils import login_client_as


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests by default.
    """
    pass


@pytest.fixture(autouse=True)
def disable_sms(settings):
    settings.SEND_SMS = False


@pytest.fixture
def json_client(client: Client) -> Client:
    """
    Configura o cliente Django para aceitar e enviar JSON.
    
    Args:
        client: O cliente Django a ser configurado.
    
    Returns:
        Client: O cliente configurado para JSON.
    """
    client.defaults['CONTENT_TYPE'] = 'application/json'
    return client


@pytest.fixture
def user_client(json_client):
    user = UserFactory.create()
    json_client = login_client_as(json_client, user)
    return json_client


@pytest.fixture
def system_client(json_client):
    system: ApiConsumer = ApiConsumerFactory.create()
    token = AuthController.get_token(system.name, "system")

    json_client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token.access_token}'

    return json_client


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

@pytest.fixture
def login_history():
    login_history = LoginHistoryFactory.create()
    return login_history

@pytest.fixture
def admin_user():
    admin = UserFactory.create(staff_level='admin')
    return admin


@pytest.fixture(scope="session", autouse=True)
def test_media_isolation():
    """
    Fixture que isola arquivos de teste em MEDIA_ROOT/tests/.
    
    Setup: Cria diretório de testes isolado e configura o MEDIA_ROOT para usar este diretório.
    Teardown: Remove completamente o diretório de testes, garantindo limpeza total.
    """
    import shutil
    from unittest.mock import patch
    
    # Caminho original do MEDIA_ROOT
    original_media_root = settings.MEDIA_ROOT
    
    # Caminho isolado para os testes
    test_media_root = os.path.join(original_media_root, "tests")
    
    # Cria o diretório de testes se não existir
    os.makedirs(test_media_root, exist_ok=True)
    
    # Aplica o patch globalmente para todos os módulos que importaram MEDIA_ROOT
    patcher = patch('django.conf.settings.MEDIA_ROOT', test_media_root)
    patcher.start()
    
    # Também aplicar patches para os módulos específicos que já importaram
    with patch('core.settings.MEDIA_ROOT', test_media_root), \
         patch('app.controllers.spreadsheet_controller.MEDIA_ROOT', test_media_root):
        
        print(f"📁 Iniciando testes com MEDIA_ROOT isolado: {test_media_root}")
        
        try:
            yield test_media_root  # Os testes executam aqui
        finally:
            # Cleanup: Remove todo o diretório de testes
            try:
                if os.path.exists(test_media_root):
                    shutil.rmtree(test_media_root)
                    print(f"🧹 Diretório de testes removido: {test_media_root}")
            except Exception as e:
                print(f"⚠️  Erro ao remover diretório de testes: {e}")
            finally:
                # Para o patcher
                patcher.stop()
                print("✅ Isolamento de testes finalizado!")


# Fixture alternativa para casos específicos onde é necessário sobrescrever o MEDIA_ROOT
@pytest.fixture
def isolated_media_root():
    """
    Fixture que retorna o caminho do MEDIA_ROOT isolado para testes.
    Use esta fixture quando precisar do caminho específico do diretório de testes.
    """
    original_media_root = settings.MEDIA_ROOT
    test_media_root = os.path.join(original_media_root, "tests")
    return test_media_root
