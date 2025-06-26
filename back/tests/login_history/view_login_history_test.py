
from django.test import Client

from app.models import LoginHistory


def test_list_login_histories(system_client: Client, login_history: LoginHistory):
    response = system_client.get('/api/login_history/', content_type='application/json')

    assert response.status_code == 200, response.content
    response_data = response.json()['data']
    
    first_item = response_data['page']['items'][0]
    assert 'user' in first_item
    assert 'timestamp' in first_item
    assert 'phone_used' in first_item