import { ApiError, apiRequest } from "./client";
import type { BackendImageInfo } from "@/lib/gaia/types";

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
  preview_url?: unknown;
  image?: {
    reference?: unknown;
  };
}

export interface UploadedImageInfo extends BackendImageInfo {
  /** Browser-displayable PNG rendered by the backend (TIFFs can't be shown by <img>). */
  previewUrl?: string | undefined;
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

export async function uploadImage(file: File, modality: BackendImageInfo["modality"]): Promise<UploadedImageInfo> {
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

    const previewUrl = typeof payload.preview_url === "string" ? payload.preview_url : undefined;
    return { reference, modality, previewUrl };
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      throw new BackendUploadRequiredError();
    }
    throw error;
  }
}
