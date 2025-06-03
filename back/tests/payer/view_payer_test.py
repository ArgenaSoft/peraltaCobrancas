from django.test import Client

from app.models import Payer
from tests.factories import PayerFactory

def test_view_payer(system_client: Client, payer: Payer):
    response = system_client.get(f'/api/payer/{payer.id}', content_type='application/json')

    assert response.status_code == 200
    assert Payer.objects.filter(name=payer.name).exists()

def test_list_payer_filtered_by_user(system_client: Client):
    for i in range(2):
        PayerFactory.create(phone=f"(44) 1234-567{i}")

    PayerFactory.create_batch(5)
    response = system_client.get(
        "/api/payer/",
        {
            "f_phone__contains": '(44)',
            "page": 1,
            "page_size": 10
        },
        content_type="application/json"
    )

    assert response.status_code == 200
    response_data = response.json()

    assert response_data['data']['paginator']['total_items'] >= 2
    returned_phones = {item['phone'] for item in response_data['data']['page']['items']}
    for phone in returned_phones:
        assert '(44)' in phone, f"Phone {phone} does not contain '(44)'"

