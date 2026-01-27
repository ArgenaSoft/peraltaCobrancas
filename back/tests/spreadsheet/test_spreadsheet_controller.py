import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.controllers.spreadsheet_controller import SpreadsheetController
from app.dtos import SpreadsheetDTO
from app.schemas.spreadsheet_schemas import SaveSpreadsheetSchema
from tests.factories import CreditorFactory


class TestSpreadsheetController:
    """Testes para o SpreadsheetController"""

    def test_process_spreadsheet_new_data(self):
        """Teste de processamento com dados novos"""
        operation_uuid = uuid4()
        
        # Cria arquivos temporários
        with tempfile.TemporaryDirectory() as temp_dir:
            operation_path = Path(temp_dir) / str(operation_uuid)
            operation_path.mkdir()
            
            # Cria CSV
            csv_path = operation_path / "spreadsheet.csv"
            csv_content = [
                "Data Vencimento,Contrato,Cliente,Credor,CPF/CNPJ,Parcela,Valor,Data Pagamento,Valor Pago,Qtd Parcelas",
                "31/12/2024,123456,João Silva,Banco ABC,12345678901,1/3,1000.00,,,3",
                "31/01/2025,123456,João Silva,Banco ABC,12345678901,2/3,1000.00,,,3"
            ]
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(csv_content))
            
            # Cria diretório de boletos
            boletos_path = operation_path / "boletos"
            boletos_path.mkdir()
            (boletos_path / "123456 PARC 1.pdf").write_bytes(b"fake pdf 1")
            (boletos_path / "123456 PARC 2.pdf").write_bytes(b"fake pdf 2")
            
            with patch('app.controllers.spreadsheet_controller.MEDIA_ROOT', temp_dir):
                result = SpreadsheetController.process_spreadsheet(operation_uuid)
            
            assert isinstance(result, SpreadsheetDTO)
            assert len(result.errors) == 0
            assert len(result.warnings) == 0

    def test_process_spreadsheet_file_not_found(self):
        """Teste quando arquivo de planilha não existe"""
        operation_uuid = uuid4()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('app.controllers.spreadsheet_controller.MEDIA_ROOT', temp_dir):
                result = SpreadsheetController.process_spreadsheet(operation_uuid)
            
            assert len(result.errors) == 1
            assert "Planilha não encontrada" in result.errors[0]

    def test_sanitize_agreement_number(self):
        """Teste da sanitização do número do acordo"""
        assert SpreadsheetController._sanitize_agreement_number("123-456") == "123456"
        assert SpreadsheetController._sanitize_agreement_number("ABC123XYZ") == "123"
        assert SpreadsheetController._sanitize_agreement_number("123456") == "123456"

    def test_sanitize_cpf_cnpj(self):
        """Teste da sanitização do CPF/CNPJ"""
        assert SpreadsheetController._sanitize_cpf_cnpj("123.456.789-01") == "12345678901"
        assert SpreadsheetController._sanitize_cpf_cnpj("12.345.678/0001-90") == "12345678000190"
        assert SpreadsheetController._sanitize_cpf_cnpj("12345678901") == "12345678901"

    def test_extract_installment_number(self):
        """Teste da extração do número da parcela"""
        assert SpreadsheetController._extract_installment_number("1/3") == 1
        assert SpreadsheetController._extract_installment_number("2") == 2
        assert SpreadsheetController._extract_installment_number("10/12") == 10

    def test_parse_due_date(self):
        """Teste do parsing da data de vencimento"""
        assert SpreadsheetController._parse_due_date("31/12/2024") == date(2024, 12, 31)
        assert SpreadsheetController._parse_due_date("01/01/2025") == date(2025, 1, 1)
        
        with pytest.raises(ValueError):
            SpreadsheetController._parse_due_date("invalid-date")

    def test_read_boletos_success(self):
        """Teste da leitura de boletos bem-sucedida"""
        operation_uuid = uuid4()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            boletos_path = Path(temp_dir) / str(operation_uuid) / "boletos"
            boletos_path.mkdir(parents=True)
            
            # Cria arquivos de boleto
            (boletos_path / "123456 PARC 1.pdf").write_bytes(b"fake pdf 1")
            (boletos_path / "123456 PARC 2.pdf").write_bytes(b"fake pdf 2")
            (boletos_path / "789012 PARC 1.pdf").write_bytes(b"fake pdf 3")
            
            with patch('app.controllers.spreadsheet_controller.MEDIA_ROOT', temp_dir):
                boletos = SpreadsheetController._read_boletos(operation_uuid)
            
            assert "123456" in boletos
            assert "789012" in boletos
            assert 1 in boletos["123456"]
            assert 2 in boletos["123456"]
            assert 1 in boletos["789012"]

    def test_read_boletos_directory_not_found(self):
        """Teste quando diretório de boletos não existe"""
        operation_uuid = uuid4()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('app.controllers.spreadsheet_controller.MEDIA_ROOT', temp_dir):
                boletos = SpreadsheetController._read_boletos(operation_uuid)
            
            assert boletos == {}

    def test_save_results_to_database_success(self):
        """Teste de salvamento bem-sucedido no banco"""
        job_id = "test-job-123"
        
        # Cria dados de teste
        save_data = SaveSpreadsheetSchema(
            payers=[],
            creditors=[]
        )
        
        with patch('app.controllers.creditor_controller.CreditorController.create') as mock_create_creditor, \
             patch('app.controllers.payer_controller.PayerController.create') as mock_create_payer:
            
            SpreadsheetController.save_results_to_database(job_id, save_data)
            
            # Verifica que não houve chamadas (dados vazios)
            mock_create_creditor.assert_not_called()
            mock_create_payer.assert_not_called()

    def test_save_creditors_with_deleted_items(self):
        """Teste salvamento de credores com itens deletados"""
        from app.schemas.spreadsheet_schemas import CreditorSchema
        
        job_id = "test-creditor-delete"
        
        creditor_to_save = CreditorSchema(
            name="Banco ABC",
            reissue_margin=5,
            readonly=False,
            deleted=False
        )
        
        creditor_to_delete = CreditorSchema(
            name="Banco XYZ",
            reissue_margin=3,
            readonly=False,
            deleted=True
        )
        
        save_data = SaveSpreadsheetSchema(
            payers=[],
            creditors=[creditor_to_save, creditor_to_delete]
        )
        
        with patch('app.controllers.creditor_controller.CreditorController.create') as mock_create:
            mock_create.return_value = CreditorFactory.build()
            
            SpreadsheetController.save_results_to_database(job_id, save_data)
            
            # Deve criar apenas 1 credor (o não deletado)
            mock_create.assert_called_once()


class TestSpreadsheetControllerErrorHandling:
    """Testes de tratamento de erros do controller"""

    def test_invalid_date_format(self):
        """Teste com formato de data inválido"""
        with pytest.raises(ValueError, match="Formato de data inválido"):
            SpreadsheetController._parse_due_date("2024-12-31")  # Formato ISO em vez de DD/MM/YYYY
            
        with pytest.raises(ValueError, match="Formato de data inválido"):
            SpreadsheetController._parse_due_date("31/13/2024")  # Mês inválido

    def test_invalid_installment_format(self):
        """Teste com formato de parcela inválido"""
        with pytest.raises(ValueError):
            SpreadsheetController._extract_installment_number("invalid")
            
        with pytest.raises(ValueError):
            SpreadsheetController._extract_installment_number("")

    @patch('app.controllers.spreadsheet_controller.lgr')
    def test_process_spreadsheet_with_csv_error(self, mock_logger):
        """Teste quando há erro ao processar CSV"""
        operation_uuid = uuid4()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            operation_path = Path(temp_dir) / str(operation_uuid)
            operation_path.mkdir()
            
            # Cria CSV corrompido
            csv_path = operation_path / "spreadsheet.csv"
            with open(csv_path, 'wb') as f:
                f.write(b'\x00\x01\x02')  # Bytes inválidos
            
            with patch('app.controllers.spreadsheet_controller.MEDIA_ROOT', temp_dir):
                result = SpreadsheetController.process_spreadsheet(operation_uuid)
            
            assert len(result.errors) > 0
            assert any("Erro ao processar planilha" in error for error in result.errors)

    def test_process_spreadsheet_general_exception(self):
        """Teste de tratamento de exceção geral"""
        operation_uuid = uuid4()
        
        with patch('pathlib.Path.exists', side_effect=Exception("File system error")):
            result = SpreadsheetController.process_spreadsheet(operation_uuid)
            
            assert len(result.errors) == 1
            assert "Erro ao processar planilha" in result.errors[0]
            assert "File system error" in result.errors[0]