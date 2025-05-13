from django.test import Client

from app.models import Creditor


def test_delete_creditor(system_client: Client, creditor: Creditor):
    response = system_client.delete(f"/api/creditor/{creditor.id}", content_type='application/json')
    assert response.status_code == 200
    assert not Creditor.objects.filter(id=creditor.id).exists(), "O Creditor não foi removido do banco de dados."
