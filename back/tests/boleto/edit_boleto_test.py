from django.test import Client

from app.models import Boleto

def test_edit_boleto(system_client: Client, boleto: Boleto):

    data = {
        'status': Boleto.Status.PAID.value
    }

    response = system_client.post(f'/api/boleto/{boleto.id}', data=data)
    response_data = response.json()

    assert response.status_code == 200, response_data
    assert response_data['data']['status'] == data['status']
    assert response_data['data']['id'] == boleto.id
