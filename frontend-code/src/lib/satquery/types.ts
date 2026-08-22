export type SlotId = string;
export type ImageModality = "optical" | "SAR";
export type BackendTask =
  | "vqa"
  | "captioning"
  | "grounding"
  | "change_vqa"
  | "optical_sar_fusion"
  | "unknown";

export interface RequiredInput {
  id: SlotId;
  code: string;
  label: string;
  hint: string;
}

export interface WorkflowComponent {
  name: string;
  role: string;
  note: string;
}

export type Intent =
  | "single_image"
  | "bitemporal"
  | "optical_sar"
  | "caption"
  | "vqa";

export interface WorkflowPlan {
  intent: Intent;
  intentLabel: string;
  workflow: string;
  understood: string;
  why: string;
  needs: string;
  next: string;
  requiredInputs: RequiredInput[];
  components: WorkflowComponent[];
}

export interface UploadedImage {
  slot: SlotId;
  file: File;
  name: string;
  modality: ImageModality;
  reference?: string;
  previewUrl: string;
  sizeBytes: number;
  format: string;
  width: number;
  height: number;
  mayCarryGeoMetadata: boolean;
  observationDate?: string;
}

export interface EvidenceItem {
  id: string;
  slot?: string;
  caption: string;
  note?: string;
}

export interface TraceStep {
  code: string;
  title: string;
  detail: string;
}

export interface BackendImageInfo {
  reference: string;
  modality: ImageModality;
}

export interface BackendEvidenceItem {
  type: string;
  data: Record<string, unknown>;
}

export interface BackendExecutionTrace {
  task_selected: string;
  execution_status: string;
  validation_result: Record<string, unknown>;
  tools_invoked: unknown[];
  errors: unknown[];
  warnings: unknown[];
}

export interface BackendAnalysisRequest {
  query: string;
  images: BackendImageInfo[];
}

export interface BackendAnalysisResponse {
  status: "success" | "failed";
  task: BackendTask;
  answer: string;
  confidence: number;
  evidence: BackendEvidenceItem[];
  execution_trace: BackendExecutionTrace;
}

export interface AnalysisResult {
  status: BackendAnalysisResponse["status"];
  task: BackendTask;
  answer: string;
  finding: string;
  meaning: string;
  observations: string[];
  evidence: BackendEvidenceItem[];
  displayEvidence: EvidenceItem[];
  confidence: { value: number; explanation: string } | null;
  execution_trace: BackendExecutionTrace;
  executionTrace: TraceStep[];
}
