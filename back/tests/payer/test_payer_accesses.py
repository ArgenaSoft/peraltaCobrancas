from django.test import Client

from app.models import Payer
from tests.utils import login_client_as


def test_human_cant_list_payers(user_client: Client):
    response = user_client.get('/api/payer/')
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_can_view_own_payer(client: Client, payer: Payer):
    user_client = login_client_as(client, payer.user)

    response = user_client.get(f"/api/payer/{payer.id}")
    response_data = response.json()
    assert response.status_code == 200, response_data


def test_human_cant_create_payer(user_client: Client):
    response = user_client.post('/api/payer/', data={})
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_delete_payer(user_client: Client):
    response = user_client.delete("/api/payer/1")
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_edit_payer(user_client: Client):
    response = user_client.patch("/api/payer/1", data={})
    response_data = response.json()
    assert response.status_code == 403, response_data
