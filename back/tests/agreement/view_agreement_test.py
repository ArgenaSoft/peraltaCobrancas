from django.test import Client

from app.models import Agreement

def test_view_agreement(system_client: Client, agreement: Agreement):
    response = system_client.get(f'/api/agreement/{agreement.id}', content_type='application/json')

    assert response.status_code == 200
    assert Agreement.objects.filter(number=agreement.number).exists()
