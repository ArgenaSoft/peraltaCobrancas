from datetime import timedelta, date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.utils import timezone

from app.models import Boleto, Installment


def test_create_boleto(system_client: Client, installment: Installment):
    pdf_content = b'%PDF-1.4\n%Fake PDF file\n1 0 obj\n<< /Type /Catalog >>\nendobj\n'
    name = "boleto.pdf"
    fake_pdf = SimpleUploadedFile(name, pdf_content, content_type="application/pdf")

    data = {
        'pdf': fake_pdf,
        'status': Boleto.Status.PENDING.value,
        'installment': installment.id,
    }

    response = system_client.post('/api/boleto/', data=data)

    response_data = response.json()
    assert response.status_code == 201, response.json()
    assert response_data['data']['pdf'].endswith(f"{installment.agreement.number}_{installment.number}.pdf")
    assert response_data['data']['status'] == data['status']
