from django.test import Client

from app.models import Boleto
from tests.factories import AgreementFactory, BoletoFactory, InstallmentFactory


def test_view_boleto(system_client: Client, boleto: Boleto):
    response = system_client.get(f'/api/boleto/{boleto.id}', content_type='application/json')

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['data']['id'] == boleto.id


def test_list_boleto_filtered_by_installment_agreement(system_client: Client):
    target_agreement = AgreementFactory.create()
    installments_target = InstallmentFactory.create_batch(5, agreement=target_agreement)
    boletos_target = [BoletoFactory.create(installment=inst) for inst in installments_target]

    # Cria boletos para outras parcelas com outros agreements
    BoletoFactory.create_batch(3)

    response = system_client.get(
        "/api/boleto/",
        {
            "f_installment__agreement__id": target_agreement.id,
            "page": 1,
            "page_size": 10
        },
        content_type="application/json"
    )

    assert response.status_code == 200
    response_data = response.json()

    assert response_data['data']['paginator']['total_items'] == 5
    returned_ids = {item['id'] for item in response_data['data']['page']['items']}
    expected_ids = {boleto.id for boleto in boletos_target}

    assert returned_ids == expected_ids
