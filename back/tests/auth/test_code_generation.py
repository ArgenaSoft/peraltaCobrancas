from django.test import Client
from app.models import LoginCode, Payer
from tests.factories import LoginCodeFactory


def test_generate_code_success(client: Client, payer: Payer):
    data = {
        "cpf": payer.user.cpf,
        "phone": payer.phone
    }
    print(data)
    response = client.get('/api/user/get_code', data)

    response_data = response.json()
    assert response.status_code == 201, response_data
    assert LoginCode.objects.filter(user=payer.user).exists(), "Código não foi criado."


def test_deny_multiple_active_codes(client: Client, payer: Payer):
    login_code = LoginCodeFactory.create(user=payer.user)
    response = client.get('/api/user/get_code', {
        "cpf": payer.user.cpf,
        "phone": payer.phone
    })

    response_data = response.json()
    assert response.status_code == 400, response_data
    assert LoginCode.objects.filter(user=payer.user).count() == 1, "Outro código foi criado indevidamente."
