import { unloggedApi } from "./baseApi";

interface GetCodeReturn {
  // TODO: NO FUTURO RETORNARÀ APENAS A MENSAGEM DE QUE O CODIGO FOI ENVIADO
  // E NÃO O CODIGO EM SI
  code: string;
}

async function callGetCode(cpf: string, phone: string): Promise<GetCodeReturn> {
  let response = await unloggedApi.get("/user/get_code", {
    params: {
      cpf: cpf,
      phone: phone
    }
  });

  return response.data;
}

interface LoginReturn {
  access: string;
  refresh: string;
  username: string;
}

async function callLogin(cpf: string, phone: string, code: string): Promise<LoginReturn> {
  let response = await unloggedApi.post("/auth/token", {
    cpf: cpf,
    phone: phone,
    code: code
  });

  return response.data;
}


async function callRefresh(refresh_token: string) {
  let response = await unloggedApi.post("/auth/refresh", {
    refresh: refresh_token
  });
  return await response.data;
}

export { callGetCode, callLogin, callRefresh };
export type { GetCodeReturn, LoginReturn };