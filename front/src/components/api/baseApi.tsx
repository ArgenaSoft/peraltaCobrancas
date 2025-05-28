import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import env from "../../../env";
import { emitSnack } from "../snackEmitter";
import { tryRefreshToken } from "../authTokenManager";

function createApi({ withAuth = false }: { withAuth?: boolean }): AxiosInstance {
  const instance = axios.create({
    baseURL: env.API_URL,
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (withAuth) {
    instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const accessToken = localStorage.getItem("access_token");
        if (accessToken) {
          config.headers["Authorization"] = `Bearer ${accessToken}`;
        }
        return config;
      },
      (error: AxiosError) => Promise.reject(error)
    );
  }

  instance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      if (!axios.isAxiosError(error)) {
        emitSnack("Erro desconhecido", "Ocorreu um erro desconhecido.", "error");
        return Promise.reject(new Error("Erro desconhecido."));
      }

      if (error.code === "ERR_NETWORK") {
        emitSnack("Erro de conexão", "Verifique sua internet.", "error");
        return Promise.reject(error);
      }

      if (error.response?.data?.message === "Token expirado") {
        const newAccessToken = await tryRefreshToken();

        if (newAccessToken) {
          const originalRequest = error.config;

          if (originalRequest?.headers) {
            originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
            return axios(originalRequest); // reenvia a requisição original
          }
        }

        emitSnack("Sessão expirada", "Faça login novamente.", "error");
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      return Promise.reject(error);
    }
  );

  return instance;
}

export const loggedApi = createApi({ withAuth: true });
export const unloggedApi = createApi({ withAuth: false });
