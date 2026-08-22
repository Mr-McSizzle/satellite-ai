import { apiRequest } from "./client";
import type {
  BackendAnalysisRequest,
  BackendAnalysisResponse,
  BackendImageInfo,
} from "@/lib/satquery/types";

export function submitAnalysis(
  query: string,
  images: BackendImageInfo[],
): Promise<BackendAnalysisResponse> {
  const body: BackendAnalysisRequest = { query, images };

  return apiRequest<BackendAnalysisResponse>("/v1/analyze", {
    method: "POST",
    body,
    timeoutMs: 120_000,
  });
}
