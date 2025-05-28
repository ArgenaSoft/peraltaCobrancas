import axios from "axios";
import { loggedApi } from "./baseApi";

import { HomeAgreement, ApiResponse, Agreement } from "@/components/types";


async function callGetHomeAgreements(): Promise<ApiResponse<HomeAgreement[]>> {
  try {
    const response = await loggedApi.get("/agreement/home");
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      // Retorna o corpo da resposta com erro (status 400, etc)
        return error.response.data as ApiResponse<HomeAgreement[]>;
    }

    throw error;
  }
}

async function callGetAgreement(number: string): Promise<ApiResponse<Agreement>> {
  try {
    const response = await loggedApi.get("/agreement/number/" + number);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      // Retorna o corpo da resposta com erro (status 400, etc)
        return error.response.data as ApiResponse<Agreement>;
    }

    throw error;
  }
}

export { callGetHomeAgreements, callGetAgreement };