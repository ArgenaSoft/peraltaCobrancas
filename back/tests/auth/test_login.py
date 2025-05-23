from datetime import timedelta
from django.test import Client
from django.utils import timezone

from app.models import Payer
from tests.factories import LoginCodeFactory


def test_login_success(client: Client, payer: Payer):
    code = "123456"
    LoginCodeFactory.create(user=payer.user, code=code, used=False)

    payload = {
        "cpf": payer.user.cpf,
        "phone": payer.phone,
        "code": code
    }

    response = client.post('/api/auth/token', data=payload, content_type='application/json')

    response_data = response.json()['data']
    assert response.status_code == 200, response_data
    assert "access" in response_data, "Token de acesso ausente na resposta."
    assert "refresh" in response_data, "Token de refresh ausente na resposta."


def test_login_fails_with_invalid_code(client: Client, payer: Payer):
    LoginCodeFactory.create(user=payer.user, code="123456", used=False)

    payload = {
        "cpf": payer.user.cpf,
        "phone": payer.phone,
        "code": "000000"
    }

    response = client.post('/api/auth/token', data=payload, content_type='application/json')
    response_data = response.json()
    assert response.status_code == 401, response_data


def test_login_fails_with_expired_code(client: Client, payer: Payer):
    expired_code = "123456"
    # Criando código com data de expiração no passado
    expired_code_obj = LoginCodeFactory.create(
        user=payer.user,
        code=expired_code,
        used=False,
        expiration_date=timezone.now() - timedelta(days=1)
    )

    payload = {
        "cpf": payer.user.cpf,
        "phone": payer.phone,
        "code": expired_code
    }

    response = client.post('/api/auth/token', data=payload, content_type='application/json')

    assert response.status_code == 401, "Esperado status 401 para código expirado."
    assert 'expirou' in response.json()['message'].lower(), "Resposta não possui a palavra chave 'expirou'"


def test_login_fails_with_used_code(client: Client, payer: Payer):
    used_code = "123456"
    # Criando código já usado
    used_code_obj = LoginCodeFactory.create(
        user=payer.user,
        code=used_code,
        used=True,
        expiration_date=timezone.now() + timedelta(hours=1)
    )

    payload = {
        "cpf": payer.user.cpf,
        "phone": payer.phone,
        "code": used_code
    }

    response = client.post('/api/auth/token', data=payload, content_type='application/json')

    assert response.status_code == 401, "Esperado status 401 para código já utilizado."
    assert 'usado' in response.json()['message'].lower(), "Mensagem de erro incorreta."


def test_login_fails_with_incorrect_phone(client: Client, payer: Payer):
    code = "123456"
    LoginCodeFactory.create(user=payer.user, code=code, used=False)

    payload = {
        "cpf": payer.user.cpf,
        "phone": "00000000000",  # Telefone incorreto
        "code": code
    }

    response = client.post('/api/auth/token', data=payload, content_type='application/json')
    assert response.status_code == 404, "Esperado status 404 para telefone incorreto."
    assert 'não encontrado' in response.json()['message'].lower(), "Mensagem de erro incorreta."


def test_login_fails_with_incorrect_cpf(client: Client, payer: Payer):
    code = "123456"
    LoginCodeFactory.create(user=payer.user, code=code, used=False)

    payload = {
        "cpf": "00000000000",  # CPF incorreto
        "phone": payer.phone,
        "code": code
    }

    response = client.post('/api/auth/token', data=payload, content_type='application/json')

    assert response.status_code == 401, "Esperado status 401 para CPF incorreto."
    assert 'cpf' in response.json()['message'].lower(), "Mensagem de erro incorreta."
