from django.test import Client

from app.models import Boleto


def test_view_boleto(system_client: Client, boleto: Boleto):
    response = system_client.get(f'/api/boleto/{boleto.id}', content_type='application/json')

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['data']['id'] == boleto.id
