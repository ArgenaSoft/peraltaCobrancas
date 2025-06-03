from pprint import pprint
from django.test import Client

from app.models import Boleto, Installment
from tests.factories import AgreementFactory, InstallmentFactory

def test_view_installment(system_client: Client, installment: Installment):
    response = system_client.get(f'/api/installment/{installment.id}', content_type='application/json')

    assert response.status_code == 200
    assert Installment.objects.filter(number=installment.number).exists()

def test_list_installment_with_boleto(system_client: Client, boleto: Boleto):
    response = system_client.get(
        f'/api/installment/',
        data={'include_rels': ['boleto']},
        content_type='application/json')

    assert response.status_code == 200
    response_data = response.json()['data']
    pprint(response_data)
    assert 'boleto' in response_data['page']['items'][0], response_data['page']['items'][0]


def test_list_installment_filtered_by_agreement(system_client: Client):
    target_agreement = AgreementFactory.create()
    
    # Cria 5 parcelas ligadas ao acordo alvo
    installments_target = InstallmentFactory.create_batch(5, agreement=target_agreement)
    
    # Cria 3 parcelas aleatórias com outros agreements
    InstallmentFactory.create_batch(3)

    response = system_client.get(
        "/api/installment/",
        {
            "f_agreement__id": target_agreement.id,
            "page": 1,
            "page_size": 10
        },
        content_type="application/json"
    )

    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data['data']['paginator']['total_items'] == 5
    returned_ids = {item['id'] for item in response_data['data']['page']['items']}
    expected_ids = {inst.id for inst in installments_target}
    
    assert returned_ids == expected_ids