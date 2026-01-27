from django.test import Client

from app.models import User


def test_admin_login(client: Client, admin_user: User):
    password = "password test"
    admin_user.set_password(password)
    admin_user.save()

    payload={
        'cpf_cnpj': admin_user.cpf_cnpj,
        'password': password
    }

    response = client.post('/api/auth/admin/token', data=payload, content_type='application/json')
    data = response.json()['data']
    assert response.status_code == 200, response.json()
    assert 'access' in data


def test_customer_cant_login_as_admin(client: Client, user: User):
    payload={
        'cpf_cnpj': user.cpf_cnpj,
        'password': 'any password'
    }
    user.set_password(payload['password'])
    user.save()

    response = client.post('/api/auth/admin/token', data=payload, content_type='application/json')
    assert response.status_code == 401, response.json()
