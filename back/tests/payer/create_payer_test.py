from django.test import Client, override_settings

from app.models import Payer


@override_settings(AUTHENTICATION_CLASSES=[])
def test_create_payer(system_client: Client):
    data = {
        'name': 'teste',
        'phone': '44920029305',
        'cpf_cnpj': '13469282072',
    }

    response = system_client.post('/api/payer/', data=data, content_type='application/json')
    assert response.status_code == 201


def teste_payer_cpf_is_unique(system_client: Client, payer: Payer):
    data = {
        'name': 'teste',
        'phone': '44920029305',
        'cpf_cnpj': payer.user.cpf_cnpj,
    }

    response = system_client.post('/api/payer/', data=data, content_type='application/json')
    assert response.status_code == 400
    assert 'cpf_cnpj' in response.json()['message']
