from django.test import Client

from app.models import Boleto


def test_delete_boleto(system_client: Client, boleto: Boleto):
    response = system_client.delete(f"/api/boleto/{boleto.id}", content_type='application/json')
    assert response.status_code == 200  
    assert not Boleto.objects.filter(id=boleto.id).exists(), "O Boleto não foi removido do banco de dados."
