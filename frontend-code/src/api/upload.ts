import { ApiError, apiRequest } from "./client";
import type { BackendImageInfo } from "@/lib/satquery/types";

export class BackendUploadRequiredError extends Error {
  constructor() {
    super(
      "Backend upload support is required. The browser cannot send local file paths to GAIA; add POST /api/v1/upload so files can be stored and returned as backend references.",
    );
    this.name = "BackendUploadRequiredError";
  }
}

interface UploadResponse {
  reference?: unknown;
  image?: {
    reference?: unknown;
  };
}

function extractReference(payload: UploadResponse): string | null {
  if (typeof payload.reference === "string" && payload.reference.trim()) {
    return payload.reference;
  }

  if (typeof payload.image?.reference === "string" && payload.image.reference.trim()) {
    return payload.image.reference;
  }

  return null;
}

export async function uploadImage(file: File, modality: BackendImageInfo["modality"]): Promise<BackendImageInfo> {
  const formData = new FormData();
  formData.set("file", file);
  formData.set("modality", modality);

  try {
    const payload = await apiRequest<UploadResponse>("/v1/upload", {
      method: "POST",
      body: formData,
      timeoutMs: 120_000,
    });

    const reference = extractReference(payload);
    if (!reference) {
      throw new Error("Upload response did not include an image reference.");
    }

    return { reference, modality };
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      throw new BackendUploadRequiredError();
    }
    throw error;
  }
}
