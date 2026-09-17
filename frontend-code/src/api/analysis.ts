import { apiRequest } from "./client";
import type {
  BackendAnalysisRequest,
  BackendAnalysisResponse,
  BackendImageInfo,
} from "@/lib/satquery/types";

export function submitAnalysis(
  query: string,
  images: BackendImageInfo[],
  sessionId?: string,
): Promise<BackendAnalysisResponse> {
  const body: BackendAnalysisRequest & { session_id?: string } = { query };
  if (sessionId) {
    body.session_id = sessionId;
  } else {
    body.images = images;
  }

  return apiRequest<BackendAnalysisResponse>("/v1/analyze", {
    method: "POST",
    body,
    timeoutMs: 120_000,
  });
}
