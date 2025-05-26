import axios from "axios";
import { loggedApi } from "./baseApi";
import { ApiResponse } from "./types";
import { Agreement } from "@/components/types";


async function callGetAgreements(): Promise<ApiResponse<Agreement[]>> {
  try {
    const response = await loggedApi.get("/agreement/home");
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      // Retorna o corpo da resposta com erro (status 400, etc)
        return error.response.data as ApiResponse<Agreement[]>;
    }

    throw error;
  }
}

export { callGetAgreements };