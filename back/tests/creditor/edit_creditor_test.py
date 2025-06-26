from django.test import Client

from app.models import Creditor

def test_edit_creditor(system_client: Client, creditor: Creditor):
    data = creditor.dict()
    data['name'] = 'Teste edição'

    response = system_client.patch(f'/api/creditor/{creditor.id}', data=data, content_type='application/json')

    assert response.status_code == 200, response.content
    assert response.json()['data']['name'] == data['name']
    assert Creditor.objects.filter(name=data['name']).exists()
