import io
import json
import zipfile
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile

from app.controllers.spreadsheet_controller import SpreadsheetController
from app.dtos import SpreadsheetDTO, PayerDTO, CreditorDTO, UserDTO
from app.models import User, Creditor, Payer, Agreement, Installment

class TestProcessSpreadsheetEndpoint:
    """Testes para o endpoint POST /api/admin/spreadsheet/process"""

    def test_process_spreadsheet_success(self, system_client):
        """Teste de processamento bem-sucedido da planilha"""
        # Cria um CSV de teste
        csv_content = (
            "Data Vencimento,Contrato,Cliente,Credor,CPF/CNPJ,Parcela,Valor,Data Pagamento,Valor Pago,Qtd Parcelas\n"
            "31/12/2024,123456,João Silva,Banco ABC,12345678901,1/3,1000.00,,,3\n"
            "31/01/2025,123456,João Silva,Banco ABC,12345678901,2/3,1000.00,,,3\n"
        )
        spreadsheet_file = SimpleUploadedFile(
            "spreadsheet.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        # Cria um ZIP de boletos de teste
        boletos_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(boletos_zip_buffer, 'w') as zip_file:
            zip_file.writestr("123456 PARC 1.pdf", b"fake pdf content 1")
            zip_file.writestr("123456 PARC 2.pdf", b"fake pdf content 2")
        boletos_zip_buffer.seek(0)
        
        boletos_file = SimpleUploadedFile(
            "boletos.zip",
            boletos_zip_buffer.getvalue(),
            content_type="application/zip"
        )

        # Mock do processamento
        mock_result = SpreadsheetDTO(
            payers=[PayerDTO(
                name="João Silva",
                user=UserDTO(cpf_cnpj="12345678901"),
                phone="12345678901",
                agreements=[]
            )],
            creditors=[],
            errors=[],
            warnings=[]
        )
        
        with patch.object(SpreadsheetController, 'process_spreadsheet', return_value=mock_result):
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
        assert data['code'] == 201
        assert 'job_id' in data['data']
        assert len(data['data']['job_id']) == 36  # UUID length

    def test_process_spreadsheet_no_new_data(self, system_client):
        """Teste quando não há novos dados para processar"""
        csv_content = (
            "Data Vencimento,Contrato,Cliente,Credor,CPF/CNPJ,Parcela,Valor,Data Pagamento,Valor Pago,Qtd Parcelas\n"
            "31/12/2024,123456,João Silva,Banco ABC,12345678901,1/3,1000.00,,,3\n"
        )
        spreadsheet_file = SimpleUploadedFile(
            "spreadsheet.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        boletos_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(boletos_zip_buffer, 'w') as zip_file:
            zip_file.writestr("test.pdf", b"fake pdf content")
        boletos_zip_buffer.seek(0)
        
        boletos_file = SimpleUploadedFile(
            "boletos.zip",
            boletos_zip_buffer.getvalue(),
            content_type="application/zip"
        )

        # Mock retornando dados vazios
        mock_result = SpreadsheetDTO(
            payers=[],
            creditors=[],
            errors=[],
            warnings=[]
        )
        
        with patch.object(SpreadsheetController, 'process_spreadsheet', return_value=mock_result):
            response = system_client.post(
                '/api/admin/spreadsheet/process',
                {
                    'spreadsheet': spreadsheet_file,
                    'boletos': boletos_file
                },
                format='multipart'
            )

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['message'] == 'Não existem novas informações a serem processadas!'

    def test_process_spreadsheet_with_errors(self, system_client):
        """Teste quando o processamento retorna erros"""
        csv_content = "invalid csv content"
        spreadsheet_file = SimpleUploadedFile(
            "spreadsheet.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        boletos_file = SimpleUploadedFile(
            "boletos.zip",
            b"invalid zip content",
            content_type="application/zip"
        )

        with patch.object(SpreadsheetController, 'process_spreadsheet', side_effect=Exception("Processing error")):
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
        assert data['code'] == 500
        assert "Erro ao processar planilha" in data['message']

    def test_process_spreadsheet_missing_files(self, system_client):
        """Teste quando arquivos obrigatórios não são enviados"""
        response = system_client.post(
            '/api/admin/spreadsheet/process',
            {},
            format='multipart'
        )

        assert response.status_code == 422  # Validation error


class TestGetSpreadsheetResultsEndpoint:
    """Testes para o endpoint GET /api/admin/spreadsheet/results/{job_id}"""

    def test_get_results_success(self, system_client):
        """Teste de busca bem-sucedida de resultados"""
        job_id = "test-job-id-123"
        
        # Mock dos resultados salvos
        mock_results = {
            "payers": [],
            "creditors": [],
            "errors": [],
            "warnings": []
        }

        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.open') as mock_open, \
             patch('json.load', return_value=mock_results):
            
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            response = system_client.get(f'/api/admin/spreadsheet/results/{job_id}')

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'data' in data
        assert 'payers' in data['data']
        assert 'creditors' in data['data']
        assert 'errors' in data['data']
        assert 'warnings' in data['data']

    def test_get_results_not_found(self, system_client):
        """Teste quando o job_id não é encontrado"""
        job_id = "nonexistent-job-id"
        
        with patch('pathlib.Path.exists', return_value=False):
            response = system_client.get(f'/api/admin/spreadsheet/results/{job_id}')

        assert response.status_code == 404
        data = response.json()
        assert data['code'] == 404
        assert 'não encontrados' in data['message']

    def test_get_results_file_read_error(self, system_client):
        """Teste quando há erro ao ler o arquivo de resultados"""
        job_id = "error-job-id"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.open', side_effect=Exception("File read error")):
            
            response = system_client.get(f'/api/admin/spreadsheet/results/{job_id}')

        assert response.status_code == 500
        data = response.json()
        assert data['code'] == 500
        assert "Erro ao carregar resultados" in data['message']

    def test_get_results_invalid_json(self, system_client):
        """Teste quando o arquivo JSON está corrompido"""
        job_id = "invalid-json-job-id"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.open') as mock_open, \
             patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0)):
            
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            response = system_client.get(f'/api/admin/spreadsheet/results/{job_id}')

        assert response.status_code == 500
        data = response.json()
        assert data['code'] == 500
        assert "Erro ao carregar resultados" in data['message']


class TestSaveResultsEndpoint:
    """Testes para o endpoint POST /api/admin/spreadsheet/save_results/{job_id}"""

    def test_save_results_success(self, system_client):
        """Teste de salvamento bem-sucedido dos resultados no banco de dados"""
        
        job_id = "test-save-job-id"
        
        # Dados de teste para salvamento
        save_data = {
            "payers": [
                {
                    "name": "João Silva",
                    "user": {
                        "cpf_cnpj": "12345678901",
                        "readonly": False
                    },
                    "phone": "12345678901",
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
                                    "boleto": None,
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
            ]
        }

        # Verifica estado inicial - não deve existir os dados
        assert not User.objects.filter(cpf_cnpj="12345678901").exists()
        assert not Creditor.objects.filter(name="Banco ABC").exists()
        assert not Payer.objects.filter(name="João Silva").exists()
        assert not Agreement.objects.filter(number="123456").exists()

        # Executa o salvamento sem mock
        response = system_client.post(
            f'/api/admin/spreadsheet/save_results/{job_id}',
            data=json.dumps(save_data),
            content_type='application/json'
        )

        # Verifica resposta da API
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data'] == 'Resultados salvos com sucesso no banco de dados.'

        # Verifica se os dados foram realmente salvos no banco
        # 1. Verifica Usuário
        user = User.objects.get(cpf_cnpj="12345678901")
        assert user.is_active is True
        assert user.staff_level == 'customer'

        # 2. Verifica Credor
        creditor = Creditor.objects.get(name="Banco ABC")
        assert creditor.reissue_margin == 5
        assert creditor.is_deleted is False

        # 3. Verifica Pagador
        payer = Payer.objects.get(name="João Silva")
        assert payer.phone == "12345678901"
        assert payer.user.cpf_cnpj == "12345678901"

        # 4. Verifica Acordo
        agreement = Agreement.objects.get(number="123456")
        assert agreement.payer == payer
        assert agreement.creditor == creditor
        assert agreement.status == 'open'

        # 5. Verifica Parcela
        installment = Installment.objects.get(agreement=agreement, number="1")
        assert installment.due_date.strftime("%Y-%m-%d") == "2024-12-31"

    def test_save_results_with_existing_data(self, system_client):
        """Teste de salvamento com dados existentes (readonly)"""
        from app.models import User, Creditor, Payer, Agreement, Installment
        from tests.factories import UserFactory, CreditorFactory, PayerFactory, AgreementFactory
        
        job_id = "test-save-existing-job-id"
        
        # Cria dados existentes no banco
        existing_user = UserFactory.create(cpf_cnpj="11111111111")
        existing_creditor = CreditorFactory.create(name="Credor Existente", reissue_margin=10)
        existing_payer = PayerFactory.create(name="Pagador Existente", user=existing_user)
        existing_agreement = AgreementFactory.create(
            number="999999",
            payer=existing_payer,
            creditor=existing_creditor
        )

        # Dados de teste misturando novos e existentes
        save_data = {
            "payers": [
                {
                    "name": "Pagador Existente",
                    "user": {
                        "cpf_cnpj": "11111111111",
                        "readonly": True  # Já existe
                    },
                    "phone": "11111111111",
                    "agreements": [
                        {
                            "number": "999999",
                            "payer_cpf_cnpj": "11111111111",
                            "creditor_name": "Credor Existente",
                            "installments": [
                                {
                                    "agreement_num": "999999",
                                    "number": 1,
                                    "due_date": "2025-01-31",
                                    "boleto": None,
                                    "readonly": False,  # Nova parcela
                                    "deleted": False
                                }
                            ],
                            "readonly": True,  # Já existe
                            "deleted": False
                        }
                    ],
                    "readonly": True,  # Já existe
                    "deleted": False
                },
                {
                    "name": "Novo Pagador",
                    "user": {
                        "cpf_cnpj": "22222222222",
                        "readonly": False  # Novo
                    },
                    "phone": "22222222222",
                    "agreements": [],
                    "readonly": False,
                    "deleted": False
                }
            ],
            "creditors": [
                {
                    "name": "Novo Credor",
                    "reissue_margin": 3,
                    "readonly": False,  # Novo
                    "deleted": False
                }
            ]
        }

        # Conta inicial de registros
        initial_user_count = User.objects.count()
        initial_creditor_count = Creditor.objects.count()
        initial_payer_count = Payer.objects.count()
        initial_agreement_count = Agreement.objects.count()
        initial_installment_count = Installment.objects.count()

        # Executa o salvamento
        response = system_client.post(
            f'/api/admin/spreadsheet/save_results/{job_id}',
            data=json.dumps(save_data),
            content_type='application/json'
        )

        # Verifica resposta
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200

        # Verifica que apenas os novos dados foram criados
        # +1 usuário novo (22222222222)
        assert User.objects.count() == initial_user_count + 1
        # +1 credor novo (Novo Credor)  
        assert Creditor.objects.count() == initial_creditor_count + 1
        # +1 pagador novo (Novo Pagador)
        assert Payer.objects.count() == initial_payer_count + 1
        # Nenhum acordo novo (readonly)
        assert Agreement.objects.count() == initial_agreement_count
        # +1 parcela nova
        assert Installment.objects.count() == initial_installment_count + 1

        # Verifica dados específicos criados
        new_user = User.objects.get(cpf_cnpj="22222222222")
        new_creditor = Creditor.objects.get(name="Novo Credor")
        new_payer = Payer.objects.get(name="Novo Pagador")
        new_installment = Installment.objects.get(agreement=existing_agreement, number="1")

        assert new_user.staff_level == 'customer'
        assert new_creditor.reissue_margin == 3
        assert new_payer.user == new_user
        assert new_installment.due_date.strftime("%Y-%m-%d") == "2025-01-31"

    def test_save_results_with_deleted_items(self, system_client):
        """Teste de salvamento ignorando itens marcados como deletados"""
        from app.models import User, Creditor, Payer
        
        job_id = "test-save-deleted-job-id"
        
        # Dados de teste com itens deletados
        save_data = {
            "payers": [
                {
                    "name": "Pagador Deletado",
                    "user": {
                        "cpf_cnpj": "33333333333",
                        "readonly": False
                    },
                    "phone": "33333333333",
                    "agreements": [],
                    "readonly": False,
                    "deleted": True  # Marcado para exclusão
                },
                {
                    "name": "Pagador Válido",
                    "user": {
                        "cpf_cnpj": "44444444444",
                        "readonly": False
                    },
                    "phone": "44444444444",
                    "agreements": [],
                    "readonly": False,
                    "deleted": False  # Deve ser criado
                }
            ],
            "creditors": [
                {
                    "name": "Credor Deletado",
                    "reissue_margin": 5,
                    "readonly": False,
                    "deleted": True  # Marcado para exclusão
                },
                {
                    "name": "Credor Válido",
                    "reissue_margin": 10,
                    "readonly": False,
                    "deleted": False  # Deve ser criado
                }
            ]
        }

        # Conta inicial de registros
        initial_user_count = User.objects.count()
        initial_creditor_count = Creditor.objects.count()
        initial_payer_count = Payer.objects.count()

        # Executa o salvamento
        response = system_client.post(
            f'/api/admin/spreadsheet/save_results/{job_id}',
            data=json.dumps(save_data),
            content_type='application/json'
        )

        # Verifica resposta
        assert response.status_code == 200

        # Verifica que apenas os itens não deletados foram criados
        # +1 usuário (44444444444) - o deletado não deve ser criado
        assert User.objects.count() == initial_user_count + 1
        # +1 credor (Credor Válido) - o deletado não deve ser criado
        assert Creditor.objects.count() == initial_creditor_count + 1
        # +1 pagador (Pagador Válido) - o deletado não deve ser criado
        assert Payer.objects.count() == initial_payer_count + 1

        # Verifica que os dados corretos foram criados
        assert User.objects.filter(cpf_cnpj="44444444444").exists()
        assert not User.objects.filter(cpf_cnpj="33333333333").exists()
        
        assert Creditor.objects.filter(name="Credor Válido").exists()
        assert not Creditor.objects.filter(name="Credor Deletado").exists()
        
        assert Payer.objects.filter(name="Pagador Válido").exists()
        assert not Payer.objects.filter(name="Pagador Deletado").exists()

    def test_save_results_invalid_data(self, system_client):
        """Teste com dados inválidos para salvamento"""
        job_id = "test-invalid-save-job-id"
        
        # Dados inválidos (faltando campos obrigatórios)
        invalid_data = {
            "payers": [
                {
                    "name": "João Silva",
                    # Faltando campos obrigatórios
                }
            ],
            "creditors": []
        }

        response = system_client.post(
            f'/api/admin/spreadsheet/save_results/{job_id}',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        assert response.status_code == 422  # Validation error

    def test_save_results_database_error(self, system_client):
        """Teste quando há erro ao salvar no banco de dados"""
        job_id = "test-db-error-job-id"
        
        save_data = {
            "payers": [],
            "creditors": []
        }

        with patch.object(SpreadsheetController, 'save_results_to_database', 
                         side_effect=Exception("Database error")):
            response = system_client.post(
                f'/api/admin/spreadsheet/save_results/{job_id}',
                data=json.dumps(save_data),
                content_type='application/json'
            )

        assert response.status_code == 500
        data = response.json()
        assert data['code'] == 500
        assert "Erro ao salvar resultados no banco" in data['message']

    def test_save_results_empty_data(self, system_client):
        """Teste com dados vazios mas válidos"""
        job_id = "test-empty-save-job-id"
        
        save_data = {
            "payers": [],
            "creditors": []
        }

        with patch.object(SpreadsheetController, 'save_results_to_database') as mock_save:
            response = system_client.post(
                f'/api/admin/spreadsheet/save_results/{job_id}',
                data=json.dumps(save_data),
                content_type='application/json'
            )

        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data'] == 'Resultados salvos com sucesso no banco de dados.'
        mock_save.assert_called_once()


class TestSpreadsheetAPIIntegration:
    """Testes de integração para o fluxo completo da API"""

    def test_complete_spreadsheet_workflow(self, system_client):
        """Teste do fluxo completo: process -> get_results -> save_results"""
        # 1. Processa a planilha
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
            zip_file.writestr("123456 PARC 1.pdf", b"fake pdf content")
        boletos_zip_buffer.seek(0)
        
        boletos_file = SimpleUploadedFile(
            "boletos.zip",
            boletos_zip_buffer.getvalue(),
            content_type="application/zip"
        )

        # Mock dos resultados
        mock_payer = PayerDTO(
            name="João Silva",
            user=UserDTO(cpf_cnpj="12345678901"),
            phone="12345678901",
            agreements=[]
        )
        
        mock_creditor = CreditorDTO(
            name="Banco ABC",
            reissue_margin=5
        )
        
        mock_result = SpreadsheetDTO(
            payers=[mock_payer],
            creditors=[mock_creditor],
            errors=[],
            warnings=[]
        )

        with patch.object(SpreadsheetController, 'process_spreadsheet', return_value=mock_result):
            process_response = system_client.post(
                '/api/admin/spreadsheet/process',
                {
                    'spreadsheet': spreadsheet_file,
                    'boletos': boletos_file
                },
                format='multipart'
            )

        assert process_response.status_code == 201
        job_id = process_response.json()['data']['job_id']

        # 2. Busca os resultados
        results_data = {
            "payers": [
                {
                    "name": "João Silva",
                    "user": {"cpf_cnpj": "12345678901", "readonly": False},
                    "phone": "12345678901",
                    "agreements": [],
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
            "errors": [],
            "warnings": []
        }

        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.open') as mock_open, \
             patch('json.load', return_value=results_data):
            
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            results_response = system_client.get(f'/api/admin/spreadsheet/results/{job_id}')

        assert results_response.status_code == 200
        assert 'data' in results_response.json()

        # 3. Salva os resultados no banco
        with patch.object(SpreadsheetController, 'save_results_to_database') as mock_save:
            save_response = system_client.post(
                f'/api/admin/spreadsheet/save_results/{job_id}',
                data=json.dumps(results_data),
                content_type='application/json'
            )

        assert save_response.status_code == 200
        assert save_response.json()['code'] == 200
        mock_save.assert_called_once()

    def test_authentication_required(self, json_client):
        """Teste que verifica se autenticação é obrigatória"""
        # Tenta acessar sem autenticação
        response = json_client.get('/api/admin/spreadsheet/results/test-job-id')
        
        # Deve retornar erro de autenticação
        assert response.status_code in [401, 403]

    def test_invalid_job_id_format(self, system_client):
        """Teste com formato inválido de job_id"""
        invalid_job_id = "invalid-format-123!"
        
        with patch('pathlib.Path.exists', return_value=False):
            response = system_client.get(f'/api/admin/spreadsheet/results/{invalid_job_id}')

        assert response.status_code == 404
        data = response.json()
        assert data['code'] == 404