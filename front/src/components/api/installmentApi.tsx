import axios from "axios";
import { loggedApi } from "./baseApi";

import { Installment, PaginatedApiResponse } from "@/components/types";

async function callGetInstallments(agreement_id: number, load_boleto: boolean = false): Promise<PaginatedApiResponse<Installment>> {
  interface Payload {
    f_agreement__id: number;
    include_rels?: string[];
  }

  try {
    let data: Payload = {
      "f_agreement__id": agreement_id
    }

    if (load_boleto) {
      data.include_rels = ['boleto']
    }

    const response = await loggedApi.get("/installment/", {params: data});
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      // Retorna o corpo da resposta com erro (status 400, etc)
        return error.response.data as PaginatedApiResponse<Installment>;
    }

    throw error;
  }
}

export { callGetInstallments };