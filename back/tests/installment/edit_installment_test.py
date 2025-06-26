from django.test import Client

from app.models import Installment

def test_edit_installment(system_client: Client, installment: Installment):
    data = installment.dict()
    data['number'] = str(int(installment.number) + 1)

    response = system_client.patch(f'/api/installment/{installment.id}', data=data, content_type='application/json')

    assert response.status_code == 200, response.content
    assert response.json()['data']['number'] == data['number']
    assert Installment.objects.filter(number=data['number']).exists()
