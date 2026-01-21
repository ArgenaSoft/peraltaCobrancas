import axios from "axios";
import { unloggedApi } from "./baseApi";
import { ApiResponse } from "../types";

async function callGetCode(cpf_cnpj: string, phone: string): Promise<ApiResponse> {
  try {
    const response = await unloggedApi.get("/user/get_code", {
      params: { cpf_cnpj, phone },
    });
    return response.data;
  } catch (error) {
    throw error;
    if (axios.isAxiosError(error) && error.response) {
      // Retorna o corpo da resposta com erro (status 400, etc)
      return error.response.data as ApiResponse;
    }
  }
}

interface LoginReturn {
  access: string;
  refresh: string;
  username: string;
}

async function callLogin(cpf_cnpj: string, phone: string, code: string): Promise<ApiResponse<LoginReturn> | ApiResponse> {
  try {
    const response = await unloggedApi.post("/auth/token", { cpf_cnpj, phone, code });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return error.response.data as ApiResponse;
    }
    throw error;
  }
}


async function callAdminLogin(cpf_cnpj: string, password: string): Promise<ApiResponse<LoginReturn> | ApiResponse> {
  try {
    const response = await unloggedApi.post("/auth/admin/token", { cpf_cnpj, password });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return error.response.data as ApiResponse;
    }
    throw error;
  }
}


async function callRefresh(refresh_token: string): Promise<ApiResponse<LoginReturn>> {
  try {
    const response = await unloggedApi.post("/auth/refresh", {
      refresh: refresh_token,
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return error.response.data as ApiResponse<LoginReturn>;
    }
    throw error;
  }
}

export { callGetCode, callLogin, callAdminLogin, callRefresh };
export type { LoginReturn };