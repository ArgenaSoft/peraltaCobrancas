from typing import List

from django.test import Client

from app.models import Boleto, User
from tests.utils import generate_multiple_boletos, login_client_as


def test_human_can_list_own_boletos(client: Client, user: User):
    user_client = login_client_as(client, user)
    user_boletos: List[Boleto] = generate_multiple_boletos(3, user)

    other_user_boletos: List[Boleto] = generate_multiple_boletos(3)

    response = user_client.get('/api/boleto/')
    response_data = response.json()
    assert response.status_code == 200, response_data

    for item in response_data['data']['page']['items']:
        assert item['installment']['agreement']['payer']['user']['id'] == user.id, item

    assert len(response_data['data']['page']['items']) == 3, response_data


def test_human_cant_access_boleto_view(user_client: Client):
    response = user_client.get("/api/boleto/1")
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_create_boleto(user_client: Client):
    response = user_client.post('/api/boleto/', data={})
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_delete_boleto(user_client: Client):
    response = user_client.delete('/api/boleto/1')
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_edit_boleto(user_client: Client):
    response = user_client.post('/api/boleto/1', data={})
    response_data = response.json()
    assert response.status_code == 403, response_data
