import { submitAnalysis } from "@/api/analysis";
import type {
  AnalysisResult,
  BackendAnalysisResponse,
  BackendEvidenceItem,
  BackendExecutionTrace,
  TraceStep,
  UploadedImage,
} from "./types";

export const STAGES = [
  {
    code: "S1",
    title: "Uploading image",
    detail: "Sending selected TIFF imagery to the backend for managed storage.",
  },
  {
    code: "S2",
    title: "Validating",
    detail: "Confirming the backend references and request payload are ready for GAIA.",
  },
  {
    code: "S3",
    title: "Running GAIA",
    detail: "Submitting the query to the backend. Task selection and routing happen server-side.",
  },
  {
    code: "S4",
    title: "Running Prithvi",
    detail: "Waiting for the backend execution trace to report any geospatial tools it invoked.",
  },
  {
    code: "S5",
    title: "Generating explanation",
    detail: "Waiting for the backend answer, evidence, confidence and audit trace.",
  },
  {
    code: "S6",
    title: "Complete",
    detail: "Rendering the backend response in the dashboard.",
  },
];

const EMPTY_TRACE: BackendExecutionTrace = {
  task_selected: "",
  execution_status: "",
  validation_result: {},
  tools_invoked: [],
  errors: [],
  warnings: [],
};

function normalizeEvidence(items: BackendAnalysisResponse["evidence"]): BackendEvidenceItem[] {
  return items.map((item, index) => {
    if (
      item &&
      typeof item === "object" &&
      "type" in item &&
      typeof item.type === "string" &&
      "data" in item &&
      item.data &&
      typeof item.data === "object" &&
      !Array.isArray(item.data)
    ) {
      return item;
    }

    return {
      type: "backend_evidence",
      data: { index, value: item },
    };
  });
}

function normalizeTrace(trace: BackendAnalysisResponse["execution_trace"]): BackendExecutionTrace {
  return {
    ...EMPTY_TRACE,
    ...trace,
    validation_result:
      trace.validation_result && typeof trace.validation_result === "object" && !Array.isArray(trace.validation_result)
        ? trace.validation_result
        : {},
    tools_invoked: Array.isArray(trace.tools_invoked) ? trace.tools_invoked : [],
    errors: Array.isArray(trace.errors) ? trace.errors : [],
    warnings: Array.isArray(trace.warnings) ? trace.warnings : [],
  };
}

function mapTrace(trace: BackendExecutionTrace): TraceStep[] {
  return [
    {
      code: "TASK",
      title: "Classifier",
      detail: trace.task_selected || "Backend did not report a selected task.",
    },
    {
      code: "STATUS",
      title: "Execution status",
      detail: trace.execution_status || "Backend did not report execution status.",
    },
    {
      code: "TOOLS",
      title: "Tools invoked",
      detail: trace.tools_invoked.length
        ? trace.tools_invoked.map((tool) => (typeof tool === "string" ? tool : JSON.stringify(tool))).join(", ")
        : "Backend reported no tools.",
    },
    {
      code: "AUDIT",
      title: "Audit",
      detail: trace.errors.length ? "Backend reported execution errors." : "No backend errors reported.",
    },
  ];
}

export async function runBackendAnalysis(query: string, images: UploadedImage[]): Promise<AnalysisResult> {
  const requestImages = images.map((image) => {
    if (!image.reference) {
      throw new Error("Image upload did not produce a backend reference.");
    }

    return {
      reference: image.reference,
      modality: image.modality,
    };
  });

  const response = await submitAnalysis(query, requestImages);
  const evidence = normalizeEvidence(response.evidence);
  const executionTrace = normalizeTrace(response.execution_trace);

  return {
    status: response.status,
    task: response.task,
    answer: response.answer,
    finding: response.answer,
    meaning: `Backend classified this request as ${response.task}.`,
    observations: [
      `Backend status: ${response.status}`,
      `Images submitted: ${requestImages.length}`,
      `Evidence items returned: ${evidence.length}`,
    ],
    evidence,
    displayEvidence: images.map((image, index) => ({
      id: `input-${index}`,
      slot: image.slot,
      caption: `${image.name} (${image.modality})`,
      note: "The backend receives this image by reference after upload.",
    })),
    confidence: {
      value: response.confidence,
      explanation: "Reported by the GAIA backend.",
    },
    execution_trace: executionTrace,
    executionTrace: mapTrace(executionTrace),
  };
}
