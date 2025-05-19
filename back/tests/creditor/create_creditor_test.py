from django.test import Client, override_settings

from app.models import Creditor


@override_settings(AUTHENTICATION_CLASSES=[])
def test_create_creditor(system_client: Client):
    data = {
        'name': 'teste',
        'reissue_margin': '2'
    }

    response = system_client.post('/api/creditor/', data=data, content_type='application/json')
    assert response.status_code == 201
