from django.test import Client

from app.models import Payer

def test_view_payer(system_client: Client, payer: Payer):
    response = system_client.get(f'/api/payer/{payer.id}', content_type='application/json')

    assert response.status_code == 200
    assert Payer.objects.filter(name=payer.name).exists()
