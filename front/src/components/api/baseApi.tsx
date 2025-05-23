import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import env from "../../../env";

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
  return instance;
}

export const loggedApi = createApi({ withAuth: true });
export const unloggedApi = createApi({ withAuth: false });