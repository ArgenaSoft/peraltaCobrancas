import io
import json
import pytest
import zipfile
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile

from app.dtos import SpreadsheetDTO, PayerDTO, UserDTO


class TestSpreadsheetProcessingEdgeCases:
    """Testes para casos extremos e cenários específicos"""

    def test_process_spreadsheet_with_warnings(self, system_client):
        """Teste quando o processamento gera warnings"""
        csv_content = (
            "Data Vencimento,Contrato,Cliente,Credor,CPF/CNPJ,Parcela,Valor,Data Pagamento,Valor Pago,Qtd Parcelas\n"
            "31/12/2024,123456,João Silva,Banco ABC,12345678901,1/3,1000.00,,,3\n"
        )
        spreadsheet_file = SimpleUploadedFile(
            "spreadsheet.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        # ZIP sem boletos para gerar warnings
        boletos_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(boletos_zip_buffer, 'w') as zip_file:
            zip_file.writestr("other_file.pdf", b"fake pdf content")
        boletos_zip_buffer.seek(0)
        
        boletos_file = SimpleUploadedFile(
            "boletos.zip",
            boletos_zip_buffer.getvalue(),
            content_type="application/zip"
        )

        mock_payer = PayerDTO(
            name="João Silva",
            user=UserDTO(cpf_cnpj="12345678901"),
            phone="12345678901",
            agreements=[]
        )
        
        mock_result = SpreadsheetDTO(
            payers=[mock_payer],
            creditors=[],
            errors=[],
            warnings=["PDF do boleto não encontrado para acordo 123456 parcela 1"]
        )

        with patch('app.controllers.spreadsheet_controller.SpreadsheetController.process_spreadsheet', 
                   return_value=mock_result):
            response = system_client.post(
                '/api/admin/spreadsheet/process',
                {
                    'spreadsheet': spreadsheet_file,
                    'boletos': boletos_file
                },
                format='multipart'
            )

        assert response.status_code == 201
        data = response.json()
        assert 'job_id' in data['data']

    def test_process_large_spreadsheet(self, system_client):
        """Teste com planilha grande (múltiplas linhas)"""
        # Cria CSV com múltiplas linhas
        csv_lines = [
            "Data Vencimento,Contrato,Cliente,Credor,CPF/CNPJ,Parcela,Valor,Data Pagamento,Valor Pago,Qtd Parcelas"
        ]
        
        for i in range(100):
            csv_lines.append(
                f"31/12/2024,{123456 + i},Cliente {i},Credor {i % 5},{12345678901 + i},1/1,1000.00,,,1"
            )
        
        csv_content = "\n".join(csv_lines)
        spreadsheet_file = SimpleUploadedFile(
            "large_spreadsheet.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        boletos_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(boletos_zip_buffer, 'w') as zip_file:
            zip_file.writestr("sample.pdf", b"fake pdf content")
        boletos_zip_buffer.seek(0)
        
        boletos_file = SimpleUploadedFile(
            "boletos.zip",
            boletos_zip_buffer.getvalue(),
            content_type="application/zip"
        )

        mock_result = SpreadsheetDTO(
            payers=[],
            creditors=[],
            errors=[],
            warnings=[]
        )

        with patch('app.controllers.spreadsheet_controller.SpreadsheetController.process_spreadsheet', 
                   return_value=mock_result):
            response = system_client.post(
                '/api/admin/spreadsheet/process',
                {
                    'spreadsheet': spreadsheet_file,
                    'boletos': boletos_file
                },
                format='multipart'
            )

        assert response.status_code == 200  # No new data
        assert 'Não existem novas informações' in response.json()['message']

    def test_process_spreadsheet_with_special_characters(self, system_client):
        """Teste com caracteres especiais nos dados"""
        csv_content = (
            "Data Vencimento,Contrato,Cliente,Credor,CPF/CNPJ,Parcela,Valor,Data Pagamento,Valor Pago,Qtd Parcelas\n"
            "31/12/2024,123456,João da Silva Ção,Banco & Cia Ltda,12345678901,1/1,1.000,00,,,1\n"
        )
        spreadsheet_file = SimpleUploadedFile(
            "spreadsheet_special.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        boletos_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(boletos_zip_buffer, 'w') as zip_file:
            zip_file.writestr("123456 PARC 1.pdf", b"fake pdf content")
        boletos_zip_buffer.seek(0)
        
        boletos_file = SimpleUploadedFile(
            "boletos.zip",
            boletos_zip_buffer.getvalue(),
            content_type="application/zip"
        )

        mock_payer = PayerDTO(
            name="João da Silva Ção",
            user=UserDTO(cpf_cnpj="12345678901"),
            phone="12345678901",
            agreements=[]
        )

        mock_result = SpreadsheetDTO(
            payers=[mock_payer],
            creditors=[],
            errors=[],
            warnings=[]
        )

        with patch('app.controllers.spreadsheet_controller.SpreadsheetController.process_spreadsheet', 
                   return_value=mock_result):
            response = system_client.post(
                '/api/admin/spreadsheet/process',
                {
                    'spreadsheet': spreadsheet_file,
                    'boletos': boletos_file
                },
                format='multipart'
            )

        assert response.status_code == 201

    def test_process_spreadsheet_invalid_zip(self, system_client):
        """Teste com arquivo ZIP inválido"""
        csv_content = (
            "Data Vencimento,Contrato,Cliente,Credor,CPF/CNPJ,Parcela,Valor,Data Pagamento,Valor Pago,Qtd Parcelas\n"
            "31/12/2024,123456,João Silva,Banco ABC,12345678901,1/1,1000.00,,,1\n"
        )
        spreadsheet_file = SimpleUploadedFile(
            "spreadsheet.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        # Arquivo que não é um ZIP válido
        invalid_zip_file = SimpleUploadedFile(
            "boletos.zip",
            b"this is not a valid zip file",
            content_type="application/zip"
        )

        response = system_client.post(
            '/api/admin/spreadsheet/process',
            {
                'spreadsheet': spreadsheet_file,
                'boletos': invalid_zip_file
            },
            format='multipart'
        )

        assert response.status_code == 500
        data = response.json()
        assert "Erro ao processar planilha" in data['message']

    def test_process_spreadsheet_empty_csv(self, system_client):
        """Teste com CSV vazio"""
        csv_content = "Data Vencimento,Contrato,Cliente,Credor,CPF/CNPJ,Parcela,Valor,Data Pagamento,Valor Pago,Qtd Parcelas\n"
        spreadsheet_file = SimpleUploadedFile(
            "empty_spreadsheet.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        boletos_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(boletos_zip_buffer, 'w') as zip_file:
            zip_file.writestr("empty.txt", b"")
        boletos_zip_buffer.seek(0)
        
        boletos_file = SimpleUploadedFile(
            "boletos.zip",
            boletos_zip_buffer.getvalue(),
            content_type="application/zip"
        )

        mock_result = SpreadsheetDTO(
            payers=[],
            creditors=[],
            errors=[],
            warnings=[]
        )

        with patch('app.controllers.spreadsheet_controller.SpreadsheetController.process_spreadsheet', 
                   return_value=mock_result):
            response = system_client.post(
                '/api/admin/spreadsheet/process',
                {
                    'spreadsheet': spreadsheet_file,
                    'boletos': boletos_file
                },
                format='multipart'
            )

        assert response.status_code == 200
        assert 'Não existem novas informações' in response.json()['message']


class TestSpreadsheetResultsValidation:
    """Testes de validação dos dados de resultados"""

    def test_get_results_with_complex_data(self, system_client):
        """Teste com dados complexos nos resultados"""
        job_id = "complex-data-job"
        
        complex_results = {
            "payers": [
                {
                    "name": "João Silva",
                    "user": {
                        "cpf_cnpj": "12345678901",
                        "readonly": False
                    },
                    "phone": "11999999999",
                    "agreements": [
                        {
                            "number": "123456",
                            "payer_cpf_cnpj": "12345678901",
                            "creditor_name": "Banco ABC",
                            "installments": [
                                {
                                    "agreement_num": "123456",
                                    "number": 1,
                                    "due_date": "2024-12-31",
                                    "boleto": {
                                        "path": "/path/to/boleto.pdf",
                                        "readonly": False
                                    },
                                    "readonly": False,
                                    "deleted": False
                                }
                            ],
                            "readonly": False,
                            "deleted": False
                        }
                    ],
                    "readonly": False,
                    "deleted": False
                }
            ],
            "creditors": [
                {
                    "name": "Banco ABC",
                    "reissue_margin": 5,
                    "readonly": False,
                    "deleted": False
                }
            ],
            "errors": ["Erro de exemplo"],
            "warnings": ["Warning de exemplo"]
        }

        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.open') as mock_open, \
             patch('json.load', return_value=complex_results):
            
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            response = system_client.get(f'/api/admin/spreadsheet/results/{job_id}')

        assert response.status_code == 200
        data = response.json()
        assert len(data['data']['errors']) == 1
        assert len(data['data']['warnings']) == 1
        assert len(data['data']['payers']) == 1
        assert data['data']['payers'][0]['name'] == "João Silva"

    def test_save_results_with_deleted_items(self, system_client):
        """Teste salvamento com itens marcados como deletados"""
        job_id = "deleted-items-job"
        
        save_data = {
            "payers": [
                {
                    "name": "Payer To Delete",
                    "user": {
                        "cpf_cnpj": "11111111111",
                        "readonly": False
                    },
                    "phone": "11111111111",
                    "agreements": [],
                    "readonly": False,
                    "deleted": True  # Marcado para exclusão
                },
                {
                    "name": "Payer To Keep",
                    "user": {
                        "cpf_cnpj": "22222222222",
                        "readonly": False
                    },
                    "phone": "22222222222",
                    "agreements": [],
                    "readonly": False,
                    "deleted": False
                }
            ],
            "creditors": [
                {
                    "name": "Creditor To Delete",
                    "reissue_margin": 5,
                    "readonly": False,
                    "deleted": True  # Marcado para exclusão
                }
            ]
        }

        with patch('app.controllers.spreadsheet_controller.SpreadsheetController.save_results_to_database') as mock_save:
            response = system_client.post(
                f'/api/admin/spreadsheet/save_results/{job_id}',
                data=json.dumps(save_data),
                content_type='application/json'
            )

        assert response.status_code == 200
        mock_save.assert_called_once()

    def test_save_results_readonly_items(self, system_client):
        """Teste salvamento com itens somente leitura"""
        job_id = "readonly-items-job"
        
        save_data = {
            "payers": [
                {
                    "name": "Existing Payer",
                    "user": {
                        "cpf_cnpj": "33333333333",
                        "readonly": True  # Item existe no banco
                    },
                    "phone": "33333333333",
                    "agreements": [
                        {
                            "number": "789012",
                            "payer_cpf_cnpj": "33333333333",
                            "creditor_name": "Existing Creditor",
                            "installments": [],
                            "readonly": True,  # Acordo existe no banco
                            "deleted": False
                        }
                    ],
                    "readonly": True,
                    "deleted": False
                }
            ],
            "creditors": []
        }

        with patch('app.controllers.spreadsheet_controller.SpreadsheetController.save_results_to_database') as mock_save:
            response = system_client.post(
                f'/api/admin/spreadsheet/save_results/{job_id}',
                data=json.dumps(save_data),
                content_type='application/json'
            )

        assert response.status_code == 200
        mock_save.assert_called_once()


class TestSpreadsheetAPIPerformance:
    """Testes de performance e limite de recursos"""

    def test_process_very_large_zip(self, system_client):
        """Teste com ZIP muito grande (simulado)"""
        csv_content = (
            "Data Vencimento,Contrato,Cliente,Credor,CPF/CNPJ,Parcela,Valor,Data Pagamento,Valor Pago,Qtd Parcelas\n"
            "31/12/2024,123456,João Silva,Banco ABC,12345678901,1/1,1000.00,,,1\n"
        )
        spreadsheet_file = SimpleUploadedFile(
            "spreadsheet.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        # Simula um ZIP muito grande com muitos arquivos
        boletos_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(boletos_zip_buffer, 'w') as zip_file:
            for i in range(1000):  # Muitos arquivos
                zip_file.writestr(f"boleto_{i}.pdf", b"fake pdf content " * 100)
        boletos_zip_buffer.seek(0)
        
        boletos_file = SimpleUploadedFile(
            "large_boletos.zip",
            boletos_zip_buffer.getvalue(),
            content_type="application/zip"
        )

        mock_result = SpreadsheetDTO(
            payers=[],
            creditors=[],
            errors=[],
            warnings=[]
        )

        with patch('app.controllers.spreadsheet_controller.SpreadsheetController.process_spreadsheet', 
                   return_value=mock_result):
            response = system_client.post(
                '/api/admin/spreadsheet/process',
                {
                    'spreadsheet': spreadsheet_file,
                    'boletos': boletos_file
                },
                format='multipart'
            )

        # Deve processar normalmente mesmo com arquivo grande
        assert response.status_code in [200, 201]

    @patch('app.controllers.spreadsheet_controller.SpreadsheetController.process_spreadsheet')
    def test_process_timeout_handling(self, mock_process, system_client):
        """Teste de tratamento de timeout no processamento"""
        csv_content = (
            "Data Vencimento,Contrato,Cliente,Credor,CPF/CNPJ,Parcela,Valor,Data Pagamento,Valor Pago,Qtd Parcelas\n"
            "31/12/2024,123456,João Silva,Banco ABC,12345678901,1/1,1000.00,,,1\n"
        )
        spreadsheet_file = SimpleUploadedFile(
            "spreadsheet.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        boletos_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(boletos_zip_buffer, 'w') as zip_file:
            zip_file.writestr("sample.pdf", b"fake pdf content")
        boletos_zip_buffer.seek(0)
        
        boletos_file = SimpleUploadedFile(
            "boletos.zip",
            boletos_zip_buffer.getvalue(),
            content_type="application/zip"
        )

        # Simula timeout
        mock_process.side_effect = TimeoutError("Processing timeout")

        response = system_client.post(
            '/api/admin/spreadsheet/process',
            {
                'spreadsheet': spreadsheet_file,
                'boletos': boletos_file
            },
            format='multipart'
        )

        assert response.status_code == 500
        data = response.json()
        assert "Erro ao processar planilha" in data['message']