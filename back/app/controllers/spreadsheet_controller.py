import csv
from datetime import date, datetime
from enum import Enum
import logging
import os
from pathlib import Path
import re
from traceback import format_exc
from typing import Dict, List, Optional, Tuple
from typing_extensions import TypedDict
from uuid import UUID

from app.controllers.boleto_controller import BoletoController
from app.controllers.creditor_controller import CreditorController
from app.controllers.payer_controller import PayerController
from app.controllers.agreement_controller import AgreementController
from app.controllers.installment_controller import InstallmentController
from app.dtos import AgreementDTO, BoletoDTO, CreditorDTO, InstallmentDTO, PayerDTO, SpreadsheetDTO, UserDTO
from app.models import Agreement, Boleto, Creditor, Installment, Payer
from app.schemas.agreement_schemas import AgreementInSchema
from app.schemas.boleto_schemas import BoletoInSchema
from app.schemas.creditor_schemas import CreditorInSchema
from app.schemas.installment_schemas import InstallmentInSchema
from app.schemas.payer_schemas import PayerInSchema
from app.schemas.spreadsheet_schemas import AgreementSchema, BoletoSchema, InstallmentSchema, SaveSpreadsheetSchema
from core.settings import MEDIA_ROOT


lgr = logging.getLogger(__name__)


class ColumnOrder(Enum):
    DUE_DATE = 0
    CONTRACT = 1
    CUSTOMER = 2
    CREDITOR = 3
    CPF_CNPJ = 4
    INSTALL_NUM = 5
    VALUE = 6
    PAYMENT_DATE = 7
    PAYMENT_VALUE = 8
    INSTALLMENTS_QTY = 9


class BoletoPdf(TypedDict):
    filepath: str
    agreement: str
    installment: int


class Cache(TypedDict):
    payers: Dict[str, PayerDTO]
    agreements: Dict[str, AgreementDTO]
    creditors: Dict[str, CreditorDTO]
    installments: Dict[Tuple[str, int], InstallmentDTO]


class RowData(TypedDict):
    creditor_name: str
    payer_name: str
    cpf_cnpj: str
    phone: str
    agreement_num: str
    installment_num: int
    due_date_str: str


class SpreadsheetController:
    
    @classmethod
    def process_spreadsheet(cls, operation_uuid: UUID) -> SpreadsheetDTO:
        """
        Processa a planilha e retorna todos os itens que precisam ser criados
        no banco de dados, sem efetivamente criá-los.
        
        Args:
            operation_uuid: UUID da operação de upload
            
        Returns:
            SpreadsheetDTO: Objeto contendo todos os itens a serem criados
        """
        result_data = SpreadsheetDTO(**{
            "creditors": [], "payers": [],
            "errors": [], "warnings": []
        })
        
        try:
            spreadsheet_path = Path(MEDIA_ROOT) / f"{operation_uuid}/spreadsheet.csv"
            
            if not spreadsheet_path.exists():
                result_data.errors.append(f"Planilha não encontrada: {spreadsheet_path}")
                return result_data
            
            # Lê os PDFs de boleto disponíveis
            boletos_pdfs = cls._read_boletos(operation_uuid)
            
            # Processa cada linha da planilha
            with open(spreadsheet_path, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)  # Pula o cabeçalho
                
                process_cache: Cache = {
                    "payers": {},
                    "agreements": {},
                    "creditors": {},
                    "installments": {}
                }
                for line_num, row in enumerate(reader, start=2):
                    try:
                        cls._process_line(row, boletos_pdfs, result_data, line_num, process_cache)
                    except Exception as e:
                        error_msg = f"Erro na linha {line_num}: {str(e)}"
                        lgr.error(error_msg)
                        result_data.errors.append(error_msg)
            
        except Exception as e:
            error_msg = f"Erro ao processar planilha: {str(e)}"
            lgr.error(error_msg)
            result_data.errors.append(error_msg)

        return result_data

    @classmethod
    def _process_line(cls, row: List[str], boletos: Dict[str, Dict[int, BoletoPdf]], result: SpreadsheetDTO, line_num: int, cache: Cache) -> None:
        """
        Processa uma linha da planilha e adiciona os itens necessários ao resultado.
        
        Args:
            row: Linha da planilha
            boletos: Dicionário com os boletos disponíveis
            result: Resultado sendo construído
            line_num: Número da linha (para logs)
            cache: Cache para evitar buscas repetidas no banco de dados
        """
        try:
            # Extrai dados da linha
            document = cls._sanitize_cpf_cnpj(row[ColumnOrder.CPF_CNPJ.value])
            row_data: RowData = {
                "creditor_name": row[ColumnOrder.CREDITOR.value].strip(),
                "payer_name": row[ColumnOrder.CUSTOMER.value].strip(),
                "cpf_cnpj": document,
                "phone": document[:11],
                "agreement_num": cls._sanitize_agreement_number(row[ColumnOrder.CONTRACT.value]),
                "installment_num": cls._extract_installment_number(row[ColumnOrder.INSTALL_NUM.value].strip()),
                "due_date_str": row[ColumnOrder.DUE_DATE.value].strip(),
            }

            # Validações básicas
            if None in row_data.values() or "" in row_data.values():
                result.errors.append(f"Linha {line_num} possui campos obrigatórios em branco")
                return
            
            payer: PayerDTO
            payer, is_new = cls._get_payer_from_line(cache, row_data)
            if is_new:
                result.add_node(payer)


            creditor: CreditorDTO
            creditor, is_new = cls._get_creditor_from_line(cache, row_data)
            if is_new:
                result.creditors.append(creditor)

            agreement: AgreementDTO
            agreement, is_new = cls._get_agreement_from_line(cache, row_data)
            print(f"{agreement.number} é novo: {is_new} ===========")
            if is_new:
                result.add_node(payer, agreement)

            installment: InstallmentDTO
            installment, is_new = cls._get_installment_from_line(cache, row_data)
            if is_new:
                result.add_node(payer, agreement, installment)

            # O boleto sempre será salvo (caso seja enviado o PDF)
            boleto: Optional[BoletoDTO] = None
            agreement_installments = boletos.get(agreement.number, {})
            if not agreement_installments:
                result.warnings.append(
                    f"Linha {line_num}: Acordo {agreement.number} não possui boletos no ZIP"
                )
            else:
                boleto_data = agreement_installments.get(installment.number)
                if boleto_data:
                    boleto = BoletoDTO(
                        path=boleto_data["filepath"],
                    )
                    lgr.debug(f"Boleto adicionado ao cache para acordo {agreement.number} parcela {installment.number}")
                else:
                    result.warnings.append(
                        f"Linha {line_num}: Parcela {installment.number} do acordo {agreement.number} não possui boleto no ZIP"
                    )
                    lgr.debug(f"Parcela {installment.number} do acordo {agreement.number} não possui boleto no ZIP")
            installment.boleto = boleto


        except Exception as e:
            error_msg = f"Erro ao processar linha {line_num}: {str(e)}"
            lgr.exception(format_exc())
            result.errors.append(error_msg)

    @classmethod
    def _get_payer_from_line(cls, cache: Cache, row_data: RowData) -> Tuple[PayerDTO, bool]:
        """
        Obtém o pagador a partir da linha da planilha, verificando o cache e o banco de dados.

        Args:
            cpf_cnpj: CPF/CNPJ do pagador
            cache: Cache para evitar buscas repetidas no banco de dados
            row_data: Dados extraídos da linha da planilha
        """
        document = row_data['cpf_cnpj']
        is_new = False
        if document in cache['payers']:
            payer = cache['payers'][document]
            lgr.debug(f"Usando pagador em cache para CPF/CNPJ {document}")
        else:
            db_payer = PayerController.get(silent=True, user__cpf_cnpj=document)
            if not db_payer:
                is_new = True
                payer = PayerDTO(
                    name=row_data['payer_name'],
                    user=UserDTO(cpf_cnpj=document),
                    phone=row_data['phone'],
                    agreements=[]
                )
                lgr.debug(f"Pagador não encontrado no banco para CPF/CNPJ {document}, criando novo DTO")
            else:
                payer = PayerDTO.from_database(db_payer)
                lgr.debug(f"Pagador encontrado no banco para CPF/CNPJ {document}")

            cache['payers'][document] = payer
            lgr.debug(f"Pagador adicionado ao cache para CPF/CNPJ {document}")
        
        return payer, is_new
    
    @classmethod
    def _get_creditor_from_line(cls, cache: Cache, row_data: RowData) -> Tuple[CreditorDTO, bool]:
        """
        Obtém o credor a partir da linha da planilha, verificando o cache e o banco de dados.
        Args:
            cache: Cache para evitar buscas repetidas no banco de dados
            row_data: Dados extraídos da linha da planilha
        """
        is_new = False
        name = row_data['creditor_name']
        if name in cache['creditors']:
            creditor = cache['creditors'][name]
            lgr.debug(f"Usando credor em cache para nome {name}")
        else:
            db_creditor = CreditorController.get(silent=True, name=name)
            if not db_creditor:
                is_new = True
                creditor = CreditorDTO(
                    name=name,
                    reissue_margin=0  # Valor padrão
                )
                lgr.debug(f"Credor não encontrado no banco para nome {name}, criando novo DTO")
            else:
                creditor = CreditorDTO.from_database(db_creditor)
                lgr.debug(f"Credor encontrado no banco para nome {name}")

            cache['creditors'][name] = creditor
            lgr.debug(f"Credor adicionado ao cache para nome {name}")

        return creditor, is_new

    @classmethod
    def _get_agreement_from_line(cls, cache: Cache, row_data: RowData) -> Tuple[AgreementDTO, bool]:
        """
        Obtém o acordo a partir da linha da planilha, verificando o cache e o banco de dados.
        Args:
            cache: Cache para evitar buscas repetidas no banco de dados
            row_data: Dados extraídos da linha da planilha
        """
        is_new = False
        document = row_data['cpf_cnpj']
        creditor_name = row_data['creditor_name']
        number = row_data['agreement_num']
        if number in cache["agreements"]:
            agreement = cache["agreements"][number]
            lgr.debug(f"Usando acordo em cache para número {number}")
        else:
            db_agreement = AgreementController.get(silent=True, number=number)
            if not db_agreement:
                is_new = True
                agreement = AgreementDTO(
                    number=number,
                    payer_cpf_cnpj=document,
                    creditor_name=creditor_name,
                    installments=[]
                )
                lgr.debug(f"Acordo não encontrado no banco para número {number}, criando novo DTO")
            else:
                agreement = AgreementDTO.from_database(db_agreement)
                lgr.debug(f"Acordo encontrado no banco para número {number}")
            
            cache["agreements"][number] = agreement
            lgr.debug(f"Acordo adicionado ao cache para número {number}")
        
        return agreement, is_new

    @classmethod
    def _get_installment_from_line(cls, cache: Cache, row_data: RowData) -> Tuple[InstallmentDTO, bool]:
        """
        Obtém a parcela a partir da linha da planilha, verificando o cache e o
        banco de dados.
        Args:
            cache: Cache para evitar buscas repetidas no banco de dados
            row_data: Dados extraídos da linha da planilha
        """
        is_new = False
        agreement_num = row_data['agreement_num']
        installment_num = row_data['installment_num']
        if (agreement_num, installment_num) in cache["installments"]:
            installment = cache["installments"][(agreement_num, installment_num)]
            lgr.debug(f"Usando parcela em cache para acordo {agreement_num} parcela {installment_num}")
        else:
            db_installment = InstallmentController.get(
                silent=True,
                agreement__number=agreement_num,
                number=installment_num,
            )
            if not db_installment:
                is_new = True
                installment = InstallmentDTO(
                    number=installment_num,
                    agreement_num=agreement_num,
                    due_date=cls._parse_due_date(row_data['due_date_str'])
                )
                lgr.debug(f"Parcela não encontrada no banco para acordo {agreement_num} parcela {installment_num}, criando novo DTO")
            else:
                installment = InstallmentDTO.from_database(db_installment)
                lgr.debug(f"Parcela encontrada no banco para acordo {agreement_num} parcela {installment_num}")
            
            cache["installments"][(agreement_num, installment_num)] = installment
            lgr.debug(f"Parcela adicionada ao cache para acordo {agreement_num} parcela {installment_num}")

        return installment, is_new

    @classmethod
    def _read_boletos(cls, operation_uuid: UUID) -> Dict[str, Dict[int, BoletoPdf]]:
        """
        Lê os PDFs de boleto disponíveis e organiza por acordo e parcela.

        Returns:
            Dicionário indexado por número do acordo, contendo dicionário 
            indexado por número da parcela com informações do boleto.
        """
        boletos_path = Path(MEDIA_ROOT) / f"{operation_uuid}/boletos"

        if not boletos_path.exists():
            lgr.warning(f"Diretório de boletos não encontrado: {boletos_path}")
            return {}

        boletos = os.listdir(boletos_path)
        data: Dict[str, Dict[int, BoletoPdf]] = {}

        for bol in boletos:
            match = re.match(r'(.*) PARC (\d+).*', bol)
            if match:
                agreement = cls._sanitize_agreement_number(match.group(1))
                installment = int(match.group(2))
                bol_data: BoletoPdf = {
                    "filepath": str(boletos_path / bol),
                    "agreement": agreement,
                    "installment": installment
                }

                if agreement not in data:
                    data[agreement] = {}
                data[agreement][installment] = bol_data
            else:
                lgr.warning(f"Não foi possível extrair dados do arquivo: {bol}")

        return data

    # Métodos utilitários
    @staticmethod
    def _sanitize_agreement_number(raw_agr: str) -> str:
        """Remove caracteres não numéricos do número do acordo."""
        return re.sub(r'\D', '', raw_agr)

    @staticmethod
    def _sanitize_cpf_cnpj(cpf_cnpj: str) -> str:
        """Remove caracteres não numéricos do CPF/CNPJ."""
        return re.sub(r'\D', '', cpf_cnpj)

    @staticmethod
    def _extract_installment_number(installment_str: str) -> int:
        """Extrai o número da parcela (formato pode ser 'X/Y' ou 'X')."""
        if '/' in installment_str:
            return int(installment_str.split('/')[0])
        return int(installment_str)

    @staticmethod
    def _parse_due_date(due_date_str: str) -> date:
        """Converte string de data no formato DD/MM/YYYY para date."""
        parts = due_date_str.split('/')
        if len(parts) != 3:
            raise ValueError(f"Formato de data inválido: {due_date_str}")
        
        day, month, year = parts
        return datetime(int(year), int(month), int(day)).date()
 
    @classmethod
    def save_results_to_database(cls, job_id: str, data: SaveSpreadsheetSchema) -> None:
        """
            Salva os resultados processados no banco de dados.

            Args:
                job_id: ID do job de processamento
                data: Dados processados a serem salvos
        """
        creditors: Dict[str, Creditor] = {}
        for raw_creditor in data.creditors:
            if raw_creditor.deleted:
                continue

            creditor_schema = CreditorInSchema(
                **raw_creditor.model_dump()
            )
            creditors[raw_creditor.name] = CreditorController.create(creditor_schema)

        for raw_payer in data.payers:
            if raw_payer.deleted:
                continue
            
            if filter(lambda a: not a.deleted, raw_payer.agreements) == []:
                lgr.debug("Nenhum acordo válido para o pagador, pulando...")
                continue

            if not raw_payer.readonly:
                lgr.debug(f"Criando pagador {raw_payer.user.cpf_cnpj}")
                payer_schema: PayerInSchema = PayerInSchema(
                    **raw_payer.model_dump(), 
                    cpf_cnpj=raw_payer.user.cpf_cnpj
                )
                saved_payer = PayerController.create(payer_schema)
            else:
                lgr.debug(f"Buscando pagador {raw_payer.user.cpf_cnpj} existente")
                saved_payer = PayerController.get(silent=False, user__cpf_cnpj=raw_payer.user.cpf_cnpj)

            cls._save_agreements(saved_payer, creditors, raw_payer.agreements)

    @classmethod
    def _save_agreements(cls, payer: Payer, creditors: Dict[str, Creditor], raw_agreements: List[AgreementSchema]) -> None:
        for raw_agree in raw_agreements:
            if raw_agree.deleted:
                continue

            if not raw_agree.readonly:
                lgr.debug(f"Criando acordo {raw_agree.number} para pagador {payer.user.cpf_cnpj}")
                agreement_schema: AgreementInSchema = AgreementInSchema(
                    **raw_agree.model_dump(),
                    payer=payer.id,
                    creditor=creditors[raw_agree.creditor_name].id
                )

                saved_agreement = AgreementController.create(agreement_schema)
            else:
                lgr.debug(f"Buscando acordo {raw_agree.number} existente")
                saved_agreement = AgreementController.get(
                    silent=False,
                    number=raw_agree.number
                )

            cls._save_installments(saved_agreement, raw_agree.installments)

    @classmethod
    def _save_installments(cls, agreement: Agreement, raw_installments: List[InstallmentSchema]):
        for raw_install in raw_installments:
            if raw_install.deleted:
                continue

            
            if not raw_install.readonly:
                lgr.debug(f"Criando parcela {raw_install.number} para acordo {agreement.number}")
                installment_schema = InstallmentInSchema(
                    number=str(raw_install.number),
                    due_date=raw_install.due_date,
                    agreement=agreement.id
                )

                saved_installment = InstallmentController.create(installment_schema)
            else:
                lgr.debug(f"Buscando parcela {raw_install.number} existente para acordo {agreement.number}")
                saved_installment = InstallmentController.get(
                    silent=False,
                    agreement__number=agreement.number,
                    number=raw_install.number
                )

            if raw_install.boleto:
                cls._save_boleto(saved_installment, raw_install.boleto)
    
    @classmethod
    def _save_boleto(cls, installment: Installment, boleto: BoletoSchema):
        with open(boleto.path, 'rb') as boleto_file:
            boleto_schema: BoletoInSchema = BoletoInSchema(
                pdf=boleto_file,
                installment=installment.id,
                status=Boleto.Status.PENDING
            )
            lgr.debug(f"Criando boleto para parcela {installment.number} do acordo {installment.agreement.number}")
            BoletoController.create(boleto_schema)
