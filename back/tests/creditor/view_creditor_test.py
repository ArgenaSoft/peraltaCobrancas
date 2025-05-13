from django.test import Client

from app.models import Creditor

def test_view_creditor(system_client: Client, creditor: Creditor):
    response = system_client.get(f'/api/creditor/{creditor.id}', content_type='application/json')

    assert response.status_code == 200
    assert Creditor.objects.filter(name=creditor.name).exists()
