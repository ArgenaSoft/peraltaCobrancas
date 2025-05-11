import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import env from "../../../env";
import { FriendlyError } from "../errors";

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

  instance.interceptors.response.use(
    (response) => {
      return response;
    },
    (error: AxiosError) => {
      if (error.response?.data?.message) {
        return Promise.reject(new FriendlyError(error.response.data.message));
      }
      return Promise.reject(
        new FriendlyError("Erro inesperado", error.message)
      );

    }
  );

  return instance;
}

export const loggedApi = createApi({ withAuth: true });
export const unloggedApi = createApi({ withAuth: false });