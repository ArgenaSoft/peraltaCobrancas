from django.test import Client, override_settings

from app.models import Agreement, Creditor, Payer


@override_settings(AUTHENTICATION_CLASSES=[])
def test_create_agreement(system_client: Client, payer: Payer, creditor: Creditor):
    data = {
        'number': '1',
        'payer': payer.id,
        'creditor': creditor.id,
    }

    response = system_client.post('/api/agreement/', data=data, content_type='application/json')
    assert response.status_code == 201

    # Teardown
    Agreement.objects.filter(number=data['number']).delete()
    assert Agreement.objects.filter(number=data['number']).exists() == False, "Teardown falhou: o Agreement não foi removido do banco de dados."

@override_settings(AUTHENTICATION_CLASSES=[])
def test_cant_create_agreement_with_empty_number(system_client: Client, payer: Payer, creditor: Creditor):
    data = {
        'number': '',
        'payer': payer.id,
        'creditor': creditor.id,
    }

    response = system_client.post('/api/agreement/', data=data, content_type='application/json')
    assert response.status_code == 422, "Deveria retornar erro 422 para número vazio"
    assert 'Input should be a valid string' == response.json()['detail'][0]['msg'], "O motivo do erro não é o esperado"

    # Teardown
    Agreement.objects.filter(number=data['number']).delete()
    assert Agreement.objects.filter(number=data['number']).exists() == False, "Teardown falhou: o Agreement não foi removido do banco de dados."
