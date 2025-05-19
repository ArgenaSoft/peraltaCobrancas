from django.test import Client

from app.models import Installment, Agreement



def test_create_installment(system_client: Client, agreement: Agreement):
    data = {
        'number': '1',
        'agreement': agreement.id,
    }

    response = system_client.post('/api/installment/', data=data, content_type='application/json')
    assert response.status_code == 201


def test_cant_create_installment_with_empty_number(system_client: Client, agreement: Agreement):
    data = {
        'number': '',
        'agreement': agreement.id,
    }

    response = system_client.post('/api/installment/', data=data, content_type='application/json')
    response_data = response.json()
    assert response.status_code == 422, response.content
    assert 'Input should be a valid string' == response_data['details'][0]['msg'], response.content
