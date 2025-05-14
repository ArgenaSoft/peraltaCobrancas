from django.test import Client

from app.models import Agreement


def test_delete_agreement(system_client: Client, agreement: Agreement):
    response = system_client.delete(f"/api/agreement/{agreement.id}", content_type='application/json')
    assert response.status_code == 200  
    assert not Agreement.objects.filter(id=agreement.id).exists(), "O Agreement não foi removido do banco de dados."
