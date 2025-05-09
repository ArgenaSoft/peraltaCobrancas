from django.test import Client, override_settings

from app.models import Payer


@override_settings(AUTHENTICATION_CLASSES=[])
def test_create_payer(system_client: Client):
    data = {
        'name': 'teste',
        'phone': '44920029305',
        'cpf': '13469282072',
    }

    response = system_client.post('/api/payer/', data=data, content_type='application/json')
    print(response.content)
    assert response.status_code == 201

    # Teardown
    Payer.objects.filter(name='teste').delete()
    assert Payer.objects.filter(name='teste').exists() == False, "Teardown falhou: o Payer não foi removido do banco de dados."


def teste_payer_cpf_is_unique(system_client: Client, payer: Payer):
    data = {
        'name': 'teste',
        'phone': '44920029305',
        'cpf': payer.user.cpf,
    }

    response = system_client.post('/api/payer/', data=data, content_type='application/json')
    assert response.status_code == 400
    assert 'cpf' in response.json()['message']
    
    # Teardown
    Payer.objects.filter(name='teste').delete()
    assert Payer.objects.filter(name='teste').exists() == False, "Teardown falhou: o Payer não foi removido do banco de dados."
