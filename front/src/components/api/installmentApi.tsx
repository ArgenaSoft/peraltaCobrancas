import axios from "axios";
import { loggedApi } from "./baseApi";

import { Installment, PaginatedApiResponse } from "@/components/types";


async function callGetInstallments(agreement_id: number): Promise<PaginatedApiResponse<Installment>> {
  try {
    let filters = {
      "agreement__id": agreement_id
    }
    const response = await loggedApi.get("/installment/", {params: filters});
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