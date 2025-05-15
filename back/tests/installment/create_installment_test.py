from django.test import Client, override_settings

from app.models import Installment, Agreement


@override_settings(AUTHENTICATION_CLASSES=[])
def test_create_installment(system_client: Client, agreement: Agreement):
    data = {
        'number': '1',
        'agreement': agreement.id,
    }

    response = system_client.post('/api/installment/', data=data, content_type='application/json')
    assert response.status_code == 201

    # Teardown
    Installment.objects.filter(number=data['number']).delete()
    assert Installment.objects.filter(number=data['number']).exists() == False, "Teardown falhou: o Installment não foi removido do banco de dados."

@override_settings(AUTHENTICATION_CLASSES=[])
def test_cant_create_installment_with_empty_number(system_client: Client, agreement: Agreement):
    data = {
        'number': '',
        'agreement': agreement.id,
    }

    response = system_client.post('/api/installment/', data=data, content_type='application/json')
    assert response.status_code == 422, "Deveria retornar erro 422 para número vazio"
    assert 'Input should be a valid string' == response.json()['detail'][0]['msg'], "O motivo do erro não é o esperado"

    # Teardown
    Installment.objects.filter(number=data['number']).delete()
    assert Installment.objects.filter(number=data['number']).exists() == False, "Teardown falhou: o Installment não foi removido do banco de dados."
