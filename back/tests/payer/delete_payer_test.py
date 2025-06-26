from django.test import Client, override_settings

from app.models import Payer


def test_delete_payer(system_client: Client, payer: Payer):
    response = system_client.delete(f"/api/payer/{payer.id}", content_type='application/json')
    assert response.status_code == 200, response.content
    assert not Payer.objects.filter(id=payer.id).exists(), "O Payer não foi removido do banco de dados."
