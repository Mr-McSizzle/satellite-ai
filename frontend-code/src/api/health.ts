import { apiRequest } from "./client";

export interface HealthResponse {
  status: string;
  service: string;
}

export function checkHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>("/health", {
    baseUrl: "",
    timeoutMs: 5_000,
  });
}
