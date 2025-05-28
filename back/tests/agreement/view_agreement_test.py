from django.test import Client

from app.models import Agreement, Payer, User
from tests.factories import AgreementFactory, PayerFactory
from tests.utils import login_client_as

def test_view_agreement(system_client: Client, agreement: Agreement):
    response = system_client.get(f'/api/agreement/{agreement.id}', content_type='application/json')

    assert response.status_code == 200
    assert Agreement.objects.filter(number=agreement.number).exists()


def test_view_agreement_by_number(client: Client, user: User):
    logged = login_client_as(client, user)
    payer: Payer = PayerFactory.create(user=user)
    agreement: Agreement = AgreementFactory.create(payer=payer)

    response = logged.get(f"/api/agreement/number/{agreement.number}", content_type='application/json')
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']['number'] == str(agreement.number)
