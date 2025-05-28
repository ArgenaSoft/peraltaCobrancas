from typing import List

from django.test import Client

from app.models import Agreement, User
from tests.utils import generate_multiple_agreements, login_client_as


def test_human_can_list_own_agreement(json_client: Client, user: User):
    user_client = login_client_as(json_client, user)
    user_agreement: List[Agreement] = generate_multiple_agreements(3, user)

    other_user_agreement: List[Agreement] = generate_multiple_agreements(3)

    response = user_client.get('/api/agreement/')
    response_data = response.json()
    assert response.status_code == 200, response_data

    for item in response_data['data']['page']['items']:
        assert item['payer']['user']['id'] == user.id, item

    assert len(response_data['data']['page']['items']) == 3, response_data


def test_human_cant_access_agreement_view(user_client: Client):
    response = user_client.get("/api/agreement/1")
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_create_agreement(user_client: Client):
    response = user_client.post('/api/agreement/', data={})
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_delete_agreement(user_client: Client):
    response = user_client.delete('/api/agreement/1')
    response_data = response.json()
    assert response.status_code == 403, response_data


def test_human_cant_edit_agreement(user_client: Client):
    response = user_client.patch('/api/agreement/1', data={})
    response_data = response.json()
    assert response.status_code == 403, response_data
