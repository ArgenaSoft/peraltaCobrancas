from typing import List
from django.test import Client

from app.models import Agreement, Payer, User
from tests.factories import AgreementFactory, PayerFactory
from tests.utils import generate_multiple_agreements, login_client_as

def test_view_agreement(system_client: Client, agreement: Agreement):
    response = system_client.get(f'/api/agreement/{agreement.id}', content_type='application/json')

    assert response.status_code == 200, response.content
    assert Agreement.objects.filter(number=agreement.number).exists()


def test_view_agreement_by_number(client: Client, user: User):
    logged = login_client_as(client, user)
    payer: Payer = PayerFactory.create(user=user)
    agreement: Agreement = AgreementFactory.create(payer=payer)

    response = logged.get(f"/api/agreement/number/{agreement.number}", content_type='application/json')
    response_data = response.json()

    assert response.status_code == 200, response.content
    assert response_data['data']['number'] == str(agreement.number)


def test_list_agreement(system_client: Client):
    agreements: List[Agreement] = generate_multiple_agreements(5)
    # Agora vou alterar o number de 3 deles pra depois fazer um filtro de substring
    for i in range(3):
        agreements[i].number = f"Test Agreement {i}"
        agreements[i].save()


    response = system_client.get(
        "/api/agreement/",
        {
            "f_number__contains": "Test Agreement",
            "page": 1,
            "page_size": 10
        },
        content_type="application/json"
    )

    assert response.status_code == 200, response.content
    response_data = response.json()

    assert response_data['data']['paginator']['total_items'] == 3