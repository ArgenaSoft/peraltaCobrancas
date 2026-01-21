import json
import logging
from pathlib import Path
from traceback import format_exc
from uuid import uuid4
from zipfile import ZipFile

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from ninja import File, UploadedFile

from app.api import CustomRouter, endpoint
from app.controllers.spreadsheet_controller import SpreadsheetController
from app.dtos import SpreadsheetDTO
from app.schemas import ReturnSchema
from app.schemas.spreadsheet_schemas import ProcessSpreadsheetResponse, SaveSpreadsheetSchema
from core.settings import MEDIA_ROOT
from core.custom_request import CustomRequest


lgr = logging.getLogger(__name__)
spreadsheet_router = CustomRouter(tags=["Planilhas"])


@spreadsheet_router.post('/process', response={201: ReturnSchema[ProcessSpreadsheetResponse]})
@endpoint("Processar planilha")
def process_spreadsheet(
    request: CustomRequest,
    spreadsheet: UploadedFile = File(...),
    boletos: UploadedFile = File(...),
    ):
    # casto para os tipos certos de arquivo
    s: InMemoryUploadedFile = spreadsheet  # type: ignore
    b: InMemoryUploadedFile = boletos  # type: ignore

    operation_uuid = uuid4()

    try:
        # Extrai os boletos
        with ZipFile(b.file) as zip_file:
            zip_file.extractall(Path(MEDIA_ROOT) / str(operation_uuid) / 'boletos')

        # Salva a planilha
        default_storage.save(f'{operation_uuid}/spreadsheet.csv', s.file)

        # Processa a planilha
        results = SpreadsheetController.process_spreadsheet(operation_uuid)
        
        if len(results.payers) == 0 and len(results.creditors) == 0:
            return ReturnSchema(
                code=200,
                message='Não existem novas informações a serem processadas!'
            )
        # Salva o resultado em JSON usando o método model_dump do Pydantic
        results_json = results.model_dump(mode='json')


        default_storage.save(
            f'{operation_uuid}/results.json',
            ContentFile(json.dumps(results_json, ensure_ascii=False, indent=2).encode('utf-8'))
        )

        return ReturnSchema(
            code=201,
            data={"job_id": str(operation_uuid)}
        )
    except Exception as e:
        lgr.error(f"Erro ao processar planilha: {str(e)}")
        return ReturnSchema(
            code=500,
            message=f'Erro ao processar planilha: {str(e)}'
        )


@spreadsheet_router.get('/results/{job_id}', response={200: ReturnSchema[SpreadsheetDTO]})
@endpoint("Obter resultados da planilha")
def get_spreadsheet_results(
    request: CustomRequest,
    job_id: str,
    ):
    try:
        results_path = Path(MEDIA_ROOT) / job_id / 'results.json'
        
        if not results_path.exists():
            return ReturnSchema(
                code=404,
                message='Resultados não encontrados para o job_id fornecido.'
            )

        # Carrega o JSON e converte para DTO
        with results_path.open('r', encoding='utf-8') as f:
            results_data = json.load(f)

        # Reconstrói o DTO a partir dos dados JSON
        results_dto = SpreadsheetDTO.model_validate(results_data)

        return ReturnSchema(
            code=200,
            data=results_dto
        )
    
    except Exception as e:
        lgr.error(f"Erro ao carregar resultados: {str(e)}")
        return ReturnSchema(
            code=500,
            message=f'Erro ao carregar resultados: {str(e)}'
        )


@spreadsheet_router.post('/save_results/{job_id}', response={200: ReturnSchema[str]})
@endpoint("Salvar no banco os dados processados")
def save_results(
    request: CustomRequest,
    job_id: str,
    data: SaveSpreadsheetSchema
):
    try:
        SpreadsheetController.save_results_to_database(job_id, data)
        return ReturnSchema(
            code=200,
            data='Resultados salvos com sucesso no banco de dados.'
        )
    except Exception as e:
        lgr.exception(format_exc())
        lgr.error(f"Erro ao salvar resultados no banco: {str(e)}")
        return ReturnSchema(
            code=500,
            message=f'Erro ao salvar resultados no banco: {str(e)}'
)
