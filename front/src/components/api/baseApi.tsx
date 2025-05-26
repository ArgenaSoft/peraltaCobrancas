import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import env from "../../../env";
import { emitSnack } from "../snackEmitter";

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
      (error: AxiosError) => {
        return Promise.reject(error);
      }
    );
  }
  // Verifica por erros de conexão
  instance.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (axios.isAxiosError(error) && error.code === 'ERR_NETWORK') {
        emitSnack("Erro de conexão", "Verifique sua internet.", "error");
        return Promise.reject(new Error("Erro de conexão. Verifique sua internet."));
      }
    });

  return instance;
}

export const loggedApi = createApi({ withAuth: true });
export const unloggedApi = createApi({ withAuth: false });