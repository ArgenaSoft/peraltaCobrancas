from django.test import Client

from app.models import Installment


def test_delete_installment(system_client: Client, installment: Installment):
    response = system_client.delete(f"/api/installment/{installment.id}", content_type='application/json')
    assert response.status_code == 200  
    assert not Installment.objects.filter(id=installment.id).exists(), "O Installment não foi removido do banco de dados."
