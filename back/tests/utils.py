from django.test import Client

from app.controllers.auth_controller import AuthController
from app.models import Agreement, Boleto, Creditor, Installment, Payer, User
from app.repositories.payer_repository import PayerRepository
from tests.factories import AgreementFactory, BoletoFactory, CreditorFactory, InstallmentFactory, PayerFactory, UserFactory


def login_client_as(client: Client, user: User):
    token = AuthController.get_token(user.id, "user")
    
    client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token.access_token}'
    return client


def generate_boleto(user: User, installment: Installment = None) -> Boleto:
    """
    Gera um boleto para o usuário fornecido.
    
    Args:
        user: O usuário para o qual o boleto será gerado.
    
    Returns:
        Boleto: O boleto gerado.
    """
    if not installment:
        payer: Payer = PayerRepository.get(user=user, silent=True)
        if not payer:
            payer = PayerFactory.create(user=user)

        creditor: Creditor = CreditorFactory.create()
        agreement: Agreement = AgreementFactory.create(creditor=creditor, payer=payer)
        installment: Installment = InstallmentFactory.create(agreement=agreement)

    boleto: Boleto = BoletoFactory.create(installment=installment)
    return boleto

def generate_multiple_boletos(count: int, user: User = None) -> list[Boleto]:
    """
    Gera múltiplos boletos para o usuário fornecido.
    Caso um usuário não seja fornecido, um novo usuário será criado.

    Args:
        count: O número de boletos a serem gerados.
        user: O usuário para o qual os boletos serão gerados.

    Returns:
        list[Boleto]: Uma lista de boletos gerados.
    """
    if not user:
        user = UserFactory.create()

    boletos = []
    installment = None
    for _ in range(count):
        boleto = generate_boleto(user, installment=installment)

        if not installment:
            # Reaproveito o installment do primeiro boleto gerado para os próximos
            installment = boleto.installment

        boletos.append(boleto)

    return boletos



def generate_installment(user: User, agreement: Agreement = None) -> Installment:
    """
    Gera uma parcela para o usuário fornecido.
    
    Args:
        user: O usuário para o qual a parcela será gerada.
    
    Returns:
        Installment: A parcela gerada.
    """
    if not agreement:
        payer: Payer = PayerRepository.get(user=user, silent=True)
        if not payer:
            payer = PayerFactory.create(user=user)
        creditor: Creditor = CreditorFactory.create()
        agreement: Agreement = AgreementFactory.create(creditor=creditor, payer=payer)

    installment: Installment = InstallmentFactory.create(agreement=agreement)
    return installment

def generate_multiple_installments(count: int, user: User = None) -> list[Installment]:
    """
    Gera múltiplos installments para o usuário fornecido.
    Caso um usuário não seja fornecido, um novo usuário será criado.

    Args:
        count: O número de installments a serem gerados.
        user: O usuário para o qual os installments serão gerados.

    Returns:
        list[Installment]: Uma lista de installments gerados.
    """
    if not user:
        user = UserFactory.create()

    installments = []
    agreement = None
    for _ in range(count):
        installment = generate_installment(user, agreement=agreement)

        if not installment:
            # Reaproveito o agreement do primeiro installment gerado para os próximos
            agreement = installment.agreement

        installments.append(installment)

    return installments

