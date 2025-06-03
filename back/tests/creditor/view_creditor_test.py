from django.test import Client

from app.models import Creditor
from tests.factories import CreditorFactory

def test_view_creditor(system_client: Client, creditor: Creditor):
    response = system_client.get(f'/api/creditor/{creditor.id}', content_type='application/json')

    assert response.status_code == 200
    assert Creditor.objects.filter(name=creditor.name).exists()


def test_list_creditor_filtered_by_name(system_client: Client):
    key_string = 'Test Creditor'
    for i in range(2):
        CreditorFactory.create(name=f"{key_string} {i}")

    CreditorFactory.create_batch(5)
    response = system_client.get(
        "/api/creditor/",
        {
            "f_name__contains": f"{key_string}",
            "page": 1,
            "page_size": 10
        },
        content_type="application/json"
    )

    assert response.status_code == 200
    response_data = response.json()

    assert response_data['data']['paginator']['total_items'] >= 2
    returned_names = {item['name'] for item in response_data['data']['page']['items']}
    for name in returned_names:
        assert f"{key_string}" in name, f"Name {name} does not contain '{key_string}'"
