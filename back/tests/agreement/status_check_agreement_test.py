"""
    Quando um boleto é atualizado, deve ser verificado se o status do acordo
    precisa ser atualizado para 'closed'. Se não houver mais parcelas com
    boleto pendente, o status do acordo é atualizado para 'closed'.
"""

from django.test import Client
from app.models import Agreement, Boleto, Creditor, Payer

def test_check_agreement_status(system_client: Client, boleto: Boleto):
    """
    'boleto' pertence a um acordo de parcela única.
    Para garantir o teste, vou primeiro atualizar boleto e acordo para os estados iniciais.

    Aí depois chamo a rota de atualização do boleto para colocar seu estado como 'paid'.
    """

    boleto.status = Boleto.Status.PENDING.value
    boleto.save()

    agreement: Agreement = boleto.installment.agreement
    agreement.status = Agreement.Status.OPEN.value
    agreement.save()

    response = system_client.post(f'/api/boleto/{boleto.id}', data={'status': Boleto.Status.PAID.value})
    response_data = response.json()
    assert response.status_code == 200, response_data

    refreshed_agreement = Agreement.objects.get(id=agreement.id)
    assert refreshed_agreement.status == Agreement.Status.CLOSED.value, "O status do acordo não foi atualizado para 'closed' após o pagamento do boleto."