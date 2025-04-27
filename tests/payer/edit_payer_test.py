from django.test import Client

from app.models import Payer

def test_edit_payer(client: Client, payer: Payer):
    data = payer.dict()
    data['name'] = 'Teste edição'

    response = client.patch(f'/api/payer/{payer.id}', data=data, content_type='application/json')

    assert response.status_code == 200  # Verificando se o status code é 200
    assert response.json()['name'] == data['name']  # Verificando se o nome foi atualizado corretamente
    assert Payer.objects.filter(name='Teste edição').exists()  # Verificando se o Payer foi atualizado no banco de dados
