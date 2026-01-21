import axios from "axios";
import { loggedApi } from "./baseApi";
import { ApiResponse } from "../types";
import { SpreadsheetSubmitResponse, SpreadsheetRetrieveResponse, SpreadsheetDataSubmitResponse, SpreadsheetDataSubmitPayload } from "./returns/spreadsheetSchemas";
import { SpreadsheetState } from "@/app/admin/spreadsheet_results/[id]/state/types";

async function callSendFiles(spreadSheet: File, boletosZip: File): Promise<ApiResponse<SpreadsheetSubmitResponse>> {
  interface Payload {
    spreadsheet: File;
    boletos: File;
  }

  try {
    let data: Payload = {
      "spreadsheet": spreadSheet,
      "boletos": boletosZip
    }

    const response = await loggedApi.post("/admin/spreadsheet/process", data, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }});
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      // Retorna o corpo da resposta com erro (status 400, etc)
        return error.response.data;
    }

    throw error;
  }
}


async function callGetResults(jobId: string): Promise<ApiResponse<SpreadsheetRetrieveResponse>> {
  try{
    let response = await loggedApi.get('/admin/spreadsheet/results/' + jobId);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      // Retorna o corpo da resposta com erro (status 400, etc)
        return error.response.data;
    }

    throw error;
  }
}


async function callSaveSpreadsheetResults(jobId: string, data: SpreadsheetDataSubmitPayload): Promise<ApiResponse<SpreadsheetDataSubmitResponse>> {
  try{
    let response = await loggedApi.post('/admin/spreadsheet/save_results/' + jobId, data);
    return response.data;
  }catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      // Retorna o corpo da resposta com erro (status 400, etc)
        return error.response.data;
    }

    throw error;
  }
}

export { callSendFiles, callGetResults, callSaveSpreadsheetResults };