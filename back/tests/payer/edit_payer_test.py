from django.test import Client

from app.models import Payer

def test_edit_payer(system_client: Client, payer: Payer):
    data = payer.dict()
    data['name'] = 'Teste edição'

    response = system_client.patch(f'/api/payer/{payer.id}', data=data, content_type='application/json')

    assert response.status_code == 200, response.content
    assert response.json()['data']['name'] == data['name']
    assert Payer.objects.filter(name=data['name']).exists()
