export type ApiResponse<T = Record<string, unknown>> = {
  code: number;
  message: string | null;
  data: T | null;
};