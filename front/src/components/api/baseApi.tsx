import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import env from "../../../env";
import { FriendlyError } from "../errors";
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

  instance.interceptors.response.use(
    (response) => {
      return response;
    },
    (error: AxiosError) => {
      if (error.response?.data?.message) {
        emitSnack(error.response.data.message, "", "error");
      }
      
      return Promise.reject(error);
    }
  );

  return instance;
}

export const loggedApi = createApi({ withAuth: true });
export const unloggedApi = createApi({ withAuth: false });