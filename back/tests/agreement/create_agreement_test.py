from django.test import Client

from app.models import Agreement, Creditor, Payer


def test_create_agreement(system_client: Client, payer: Payer, creditor: Creditor):
    data = {
        'number': '1',
        'payer': payer.id,
        'creditor': creditor.id,
    }

    response = system_client.post('/api/agreement/', data=data, content_type='application/json')
    print(response.content)
    assert response.status_code == 201

    # Teardown
    Agreement.objects.filter(number=data['number']).delete()
    assert Agreement.objects.filter(number=data['number']).exists() == False, "Teardown falhou: o Agreement não foi removido do banco de dados."


def test_cant_create_agreement_with_empty_number(system_client: Client, payer: Payer, creditor: Creditor):
    data = {
        'number': '',
        'payer': payer.id,
        'creditor': creditor.id,
    }

    response = system_client.post('/api/agreement/', data=data, content_type='application/json')
    response_data = response.json()
    assert response.status_code == 422, "Deveria retornar erro 422 para número vazio"
    assert 'Input should be a valid string' == response_data['details'][0]['msg'], response_data

    # Teardown
    Agreement.objects.filter(number=data['number']).delete()
    assert Agreement.objects.filter(number=data['number']).exists() == False, "Teardown falhou: o Agreement não foi removido do banco de dados."
