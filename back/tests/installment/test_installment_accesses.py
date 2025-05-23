from typing import List
from django.test import Client

from app.models import Installment, User
from tests.utils import generate_multiple_installments, login_client_as


def test_human_can_list_own_installments(client: Client, user: User):
    user_client = login_client_as(client, user)
    user_installments: List[Installment] = generate_multiple_installments(3, user)

    other_user_installments: List[Installment] = generate_multiple_installments(3)

    response = user_client.get('/api/installment/')
    response_data = response.json()
    assert response.status_code == 200, response_data

    for item in response_data['data']['page']['items']:
        assert item['agreement']['payer']['user']['id'] == user.id, item

    assert len(response_data['data']['page']['items']) == 3, response_data


def test_human_cant_view_installment(user_client: Client):
    response = user_client.get("/api/installment/1")
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_create_installment(user_client: Client):
    response = user_client.post('/api/installment/', data={})
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_delete_installment(user_client: Client):
    response = user_client.delete("/api/installment/1")
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_edit_installment(user_client: Client):
    response = user_client.patch("/api/installment/1", data={})
    response_data = response.json()
    assert response.status_code == 403, response_data
