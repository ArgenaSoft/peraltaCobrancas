from django.test import Client

from app.models import Agreement

def test_edit_agreement(system_client: Client, agreement: Agreement):
    data = agreement.dict()
    data['number'] = str(int(agreement.number) + 1)

    response = system_client.patch(f'/api/agreement/{agreement.id}', data=data, content_type='application/json')

    assert response.status_code == 200
    assert response.json()['number'] == data['number']
    assert Agreement.objects.filter(number=data['number']).exists()
