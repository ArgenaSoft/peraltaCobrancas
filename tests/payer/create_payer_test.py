from django.test import Client

from app.models import Payer

def test_create_payer(client: Client):
    data = {
        'name': 'teste',
        'phone': '44920029305',
        'cpf': '13469282072',
    }

    response = client.post('/api/payer/', data=data, content_type='application/json')
    assert response.status_code == 201

    # Teardown
    Payer.objects.filter(name='teste').delete()
    assert Payer.objects.filter(name='teste').exists() == False, "Teardown falhou: o Payer não foi removido do banco de dados."

def teste_payer_cpf_is_unique(client: Client, payer):
    data = {
        'name': 'teste',
        'phone': '44920029305',
        'cpf': payer.cpf,
    }

    response = client.post('/api/payer/', data=data, content_type='application/json')
    assert response.status_code == 400
    assert response.json() == {'cpf': ['Payer with this cpf already exists.']}
    # Teardown
    Payer.objects.filter(name='teste').delete()
    assert Payer.objects.filter(name='teste').exists() == False, "Teardown falhou: o Payer não foi removido do banco de dados."
