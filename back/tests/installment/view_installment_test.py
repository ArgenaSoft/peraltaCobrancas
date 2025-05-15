from django.test import Client

from app.models import Installment

def test_view_installment(system_client: Client, installment: Installment):
    response = system_client.get(f'/api/installment/{installment.id}', content_type='application/json')

    assert response.status_code == 200
    assert Installment.objects.filter(number=installment.number).exists()
