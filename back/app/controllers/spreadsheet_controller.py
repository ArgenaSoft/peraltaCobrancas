from datetime import date, datetime
from enum import Enum
from io import TextIOWrapper
from pathlib import Path
from traceback import format_exc
from typing import Dict, List, Tuple
from typing_extensions import TypedDict
from uuid import UUID
import csv
import logging
import os
import re
import shutil

from app.controllers.boleto_controller import BoletoController
from app.controllers.creditor_controller import CreditorController
from app.controllers.payer_controller import PayerController
from app.controllers.agreement_controller import AgreementController
from app.controllers.installment_controller import InstallmentController
from app.dtos import AgreementDTO, BoletoDTO, CreditorDTO, InstallmentDTO, PayerDTO, SpreadsheetDTO, UserDTO
from app.exceptions import HttpFriendlyException, InvalidCsvDelimiterException
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
        result_data = SpreadsheetDTO(**{
            "payers": [], "errors": [], "warnings": []
        })

        try:
            spreadsheet_path = Path(MEDIA_ROOT) / f"{operation_uuid}/spreadsheet.csv"

            if not spreadsheet_path.exists():
                result_data.errors.append(f"Planilha não encontrada: {spreadsheet_path}")
                return result_data

            boletos_pdfs = cls._read_boletos(operation_uuid)

            with open(spreadsheet_path, "r", encoding="latin-1") as file:
                delimiter = cls._determine_csv_delimiter(file)
                reader = csv.reader(file, delimiter=delimiter)
                next(reader)
                rows = list(reader)

            process_cache = cls._build_cache(rows)

            for line_num, row in enumerate(rows, start=2):
                lgr.debug("Processando linha %d: %s", line_num, row)
                try:
                    cls._process_line(row, boletos_pdfs, result_data, line_num, process_cache)
                except Exception as e:
                    error_msg = f"Erro na linha {line_num}: {str(e)}"
                    lgr.error(error_msg)
                    result_data.errors.append(error_msg)

        except HttpFriendlyException as hfe:
            error_msg = f"Erro ao processar planilha: {hfe.message}"
            lgr.error(error_msg)
            raise hfe
        except Exception as e:
            error_msg = f"Erro ao processar planilha: {str(e)}"
            lgr.error(error_msg)
            result_data.errors.append(error_msg)

        result_data.payers = sorted(result_data.payers, key=lambda x: x.name)
        return result_data

    @classmethod
    def _build_cache(cls, rows: List[List[str]]) -> Cache:
        """
        Pré-carrega todos os dados relevantes do banco em 4 queries,
        evitando N queries dentro do loop de processamento.
        """
        required_cols = max(m.value for m in ColumnOrder) + 1
        agreement_numbers = set()
        cpf_cnpjs = set()
        creditor_names = set()

        for row in rows:
            if len(row) < required_cols:
                continue
            agreement_numbers.add(cls._sanitize_agreement_number(row[ColumnOrder.CONTRACT.value]))
            cpf_cnpjs.add(cls._sanitize_cpf_cnpj(row[ColumnOrder.CPF_CNPJ.value]))
            creditor_names.add(row[ColumnOrder.CREDITOR.value].strip())

        cache: Cache = {
            "payers": {
                p.user.cpf_cnpj: PayerDTO.from_database(p)
                for p in PayerController.filter(user__cpf_cnpj__in=cpf_cnpjs)
            },
            "creditors": {
                c.name: CreditorDTO.from_database(c)
                for c in CreditorController.filter(name__in=creditor_names)
            },
            "agreements": {
                a.number: AgreementDTO.from_database(a)
                for a in AgreementController.filter(number__in=agreement_numbers)
            },
            "installments": {
                (i.agreement.number, int(i.number)): InstallmentDTO.from_database(i)
                for i in InstallmentController.filter(
                    agreement__number__in=agreement_numbers
                ).select_related('agreement')
            },
        }

        lgr.debug(
            "Cache pré-carregado: %d pagadores, %d credores, %d acordos, %d parcelas",
            len(cache["payers"]), len(cache["creditors"]),
            len(cache["agreements"]), len(cache["installments"])
        )
        return cache

    @classmethod
    def save_results_to_database(cls, job_id: str, data: SaveSpreadsheetSchema) -> None:
        new_creditors: Dict[str, Creditor] = {}
        for raw_creditor in data.creditors:
            if raw_creditor.deleted:
                continue
            creditor_schema = CreditorInSchema(**raw_creditor.model_dump())
            new_creditors[raw_creditor.name] = CreditorController.create(creditor_schema)

        for raw_payer in data.payers:
            if raw_payer.deleted:
                continue

            if list(filter(lambda a: not a.deleted, raw_payer.agreements)) == []:
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

            cls._save_agreements(saved_payer, new_creditors, raw_payer.agreements)
        
        cls._cleanup_operation_files(job_id)

    @classmethod
    def _cleanup_operation_files(cls, operation_uuid: str) -> None:
        operation_path = Path(MEDIA_ROOT) / str(operation_uuid)
        if operation_path.exists():
            shutil.rmtree(operation_path)
            lgr.info(f"Arquivos temporários removidos: {operation_path}")
        else:
            lgr.warning(f"Diretório de operação não encontrado para limpeza: {operation_path}")


    @classmethod
    def _determine_csv_delimiter(cls, file: TextIOWrapper) -> str:
        sample = file.readline()
        file.seek(0)

        semicolon_count = sample.count(";")
        comma_count = sample.count(",")
        if semicolon_count == 9:
            return ";"
        elif comma_count == 9 or sample[-2] == ",":
            return ","
        else:
            raise InvalidCsvDelimiterException()

    @classmethod
    def _process_line(cls, row: List[str], boletos: Dict[str, Dict[int, BoletoPdf]], result: SpreadsheetDTO, line_num: int, cache: Cache) -> None:
        try:
            required_cols = max(m.value for m in ColumnOrder) + 1
            if len(row) < required_cols:
                missing_cols = [m.name for m in ColumnOrder if m.value >= len(row)]
                msg = (
                    f"Linha {line_num} possui colunas insuficientes: esperado {required_cols}, "
                    f"encontrado {len(row)}; colunas faltando: {', '.join(missing_cols)}"
                )
                lgr.error(msg)
                result.errors.append(msg)
                return

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

            empties = any(v is None or (isinstance(v, str) and v.strip() == "") for v in row_data.values())
            if empties:
                result.errors.append(f"Linha {line_num} possui campos obrigatórios em branco ou apenas espaços")
                return

            payer, is_new = cls._get_payer_from_line(cache, row_data)
            if is_new:
                result.add_node(payer)

            creditor, is_new_creditor = cls._get_creditor_from_line(cache, row_data)
            if is_new_creditor:
                result.add_creditor(creditor)

            agreement, is_new_agreement = cls._get_agreement_from_line(cache, row_data)
            if is_new_agreement:
                result.add_node(payer, agreement)

            installment, is_new_installment = cls._get_installment_from_line(cache, row_data)
            if is_new_installment:
                result.add_node(payer, agreement, installment)
                result.add_creditor(creditor)

            agreement_key = cls._sanitize_agreement_number(str(agreement.number))
            agreement_installments = boletos.get(agreement_key, {})
            if not agreement_installments:
                result.warnings.append(
                    f"Linha {line_num}: Acordo {agreement.number} não possui boletos no ZIP"
                )
            else:
                boleto_data = agreement_installments.get(installment.number)
                if boleto_data:
                    boleto = BoletoDTO(path=boleto_data["filepath"])
                    installment.boleto = boleto
                    if not is_new_installment:
                        result.add_node(payer, agreement, installment)
                    lgr.debug(f"Boleto adicionado para acordo {agreement.number} parcela {installment.number}")
                else:
                    result.warnings.append(
                        f"Linha {line_num}: Parcela {installment.number} do acordo {agreement.number} não possui boleto no ZIP"
                    )
                    lgr.debug(f"Parcela {installment.number} do acordo {agreement.number} não possui boleto no ZIP")

        except Exception as e:
            error_msg = f"Erro ao processar linha {line_num}: {str(e)}"
            lgr.exception(format_exc())
            result.errors.append(error_msg)

    @classmethod
    def _get_payer_from_line(cls, cache: Cache, row_data: RowData) -> Tuple[PayerDTO, bool]:
        document = row_data['cpf_cnpj']
        if document in cache['payers']:
            lgr.debug(f"Usando pagador em cache para CPF/CNPJ {document}")
            return cache['payers'][document], False

        is_new = True
        payer = PayerDTO(
            name=row_data['payer_name'],
            user=UserDTO(cpf_cnpj=document),
            phone=row_data['phone'],
            agreements=[]
        )
        cache['payers'][document] = payer
        lgr.debug(f"Pagador não encontrado no banco para CPF/CNPJ {document}, criando novo DTO")
        return payer, is_new

    @classmethod
    def _get_creditor_from_line(cls, cache: Cache, row_data: RowData) -> Tuple[CreditorDTO, bool]:
        name = row_data['creditor_name']
        if name in cache['creditors']:
            lgr.debug(f"Usando credor em cache para nome {name}")
            return cache['creditors'][name], False

        creditor = CreditorDTO(name=name, reissue_margin=0)
        cache['creditors'][name] = creditor
        lgr.debug(f"Credor não encontrado no banco para nome {name}, criando novo DTO")
        return creditor, True

    @classmethod
    def _get_agreement_from_line(cls, cache: Cache, row_data: RowData) -> Tuple[AgreementDTO, bool]:
        number = row_data['agreement_num']
        if number in cache["agreements"]:
            lgr.debug(f"Usando acordo em cache para número {number}")
            return cache["agreements"][number], False

        agreement = AgreementDTO(
            number=number,
            payer_cpf_cnpj=row_data['cpf_cnpj'],
            creditor_name=row_data['creditor_name'],
            installments=[]
        )
        cache["agreements"][number] = agreement
        lgr.debug(f"Acordo não encontrado no banco para número {number}, criando novo DTO")
        return agreement, True

    @classmethod
    def _get_installment_from_line(cls, cache: Cache, row_data: RowData) -> Tuple[InstallmentDTO, bool]:
        agreement_num = row_data['agreement_num']
        installment_num = row_data['installment_num']
        key = (agreement_num, installment_num)

        if key in cache["installments"]:
            lgr.debug(f"Usando parcela em cache para acordo {agreement_num} parcela {installment_num}")
            return cache["installments"][key], False

        installment = InstallmentDTO(
            number=installment_num,
            agreement_num=agreement_num,
            due_date=cls._parse_due_date(row_data['due_date_str'])
        )
        cache["installments"][key] = installment
        lgr.debug(f"Parcela não encontrada no banco para acordo {agreement_num} parcela {installment_num}, criando novo DTO")
        return installment, True

    @classmethod
    def _read_boletos(cls, operation_uuid: UUID) -> Dict[str, Dict[int, BoletoPdf]]:
        boletos_path = Path(MEDIA_ROOT) / f"{operation_uuid}/boletos"

        if not boletos_path.exists():
            lgr.warning(f"Diretório de boletos não encontrado: {boletos_path}")
            return {}

        data: Dict[str, Dict[int, BoletoPdf]] = {}
        for bol in os.listdir(boletos_path):
            match = re.match(r'(.*) PARC (\d+).*', bol)
            if match:
                agreement = cls._sanitize_agreement_number(match.group(1))
                installment = int(match.group(2))
                if agreement not in data:
                    data[agreement] = {}
                data[agreement][installment] = {
                    "filepath": str(boletos_path / bol),
                    "agreement": agreement,
                    "installment": installment
                }
            else:
                lgr.warning(f"Não foi possível extrair dados do arquivo: {bol}")

        return data

    @staticmethod
    def _sanitize_agreement_number(raw_agr: str) -> str:
        return re.sub(r'\D', '', raw_agr)

    @staticmethod
    def _sanitize_cpf_cnpj(cpf_cnpj: str) -> str:
        return re.sub(r'\D', '', cpf_cnpj)

    @staticmethod
    def _extract_installment_number(installment_str: str) -> int:
        if '/' in installment_str:
            return int(installment_str.split('/')[0])
        return int(installment_str)

    @staticmethod
    def _parse_due_date(due_date_str: str) -> date:
        parts = due_date_str.split('/')
        if len(parts) != 3:
            raise ValueError(f"Formato de data inválido: {due_date_str}")
        day, month, year = parts
        return datetime(int(year), int(month), int(day)).date()

    @classmethod
    def _save_agreements(cls, payer: Payer, new_creditors: Dict[str, Creditor], raw_agreements: List[AgreementSchema]) -> None:
        for raw_agree in raw_agreements:
            if raw_agree.deleted:
                continue

            if not raw_agree.readonly:
                lgr.debug(f"Criando acordo {raw_agree.number} para pagador {payer.user.cpf_cnpj}")
                creditor = new_creditors.get(
                    raw_agree.creditor_name,
                    CreditorController.get(silent=False, name=raw_agree.creditor_name)
                )
                if not creditor:
                    raise HttpFriendlyException(
                        404,
                        f"Credor {raw_agree.creditor_name} não encontrado ao criar acordo {raw_agree.number}"
                    )
                agreement_schema: AgreementInSchema = AgreementInSchema(
                    **raw_agree.model_dump(),
                    payer=payer.id,
                    creditor=new_creditors[raw_agree.creditor_name].id
                )
                saved_agreement = AgreementController.create(agreement_schema)
            else:
                lgr.debug(f"Buscando acordo {raw_agree.number} existente")
                saved_agreement = AgreementController.get(silent=False, number=raw_agree.number)

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
        try:
            boleto_path = Path(boleto.path)
            if not boleto_path.exists() or not boleto_path.is_file():
                lgr.error(f"Arquivo do boleto não encontrado: {boleto_path} (acordo={getattr(installment.agreement, 'number', None)} parcela={installment.number})")
                raise HttpFriendlyException(404, f"Arquivo do boleto não encontrado: {boleto_path}")

            lgr.debug(f"Salvando boleto: agreement={getattr(installment.agreement, 'number', None)} installment={installment.number} path={boleto_path}")
            with open(boleto_path, 'rb') as boleto_file:
                boleto_schema: BoletoInSchema = BoletoInSchema(
                    pdf=boleto_file,
                    installment=installment.id,
                    status=Boleto.Status.PENDING
                )
                BoletoController.create(boleto_schema)
        except HttpFriendlyException:
            raise
        except Exception as e:
            lgr.exception(f"Erro ao salvar boleto (acordo={getattr(installment.agreement, 'number', None)} parcela={getattr(installment, 'number', None)} path={getattr(boleto, 'path', None)}): {e}")
            raise