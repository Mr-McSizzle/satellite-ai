import type { Intent, WorkflowPlan } from "./types";

const CHANGE_KEYWORDS = [
  "change",
  "changed",
  "before and after",
  "difference",
  "deforestation",
  "urbanization",
  "urban growth",
  "flood",
  "damage",
  "destroyed",
  "built",
  "construction",
  "demolished",
  "temporal",
];

const SAR_KEYWORDS = [
  "sar",
  "radar",
  "synthetic aperture",
  "optical and radar",
  "radar and optical",
  "microwave",
  "sentinel-1",
  "risat",
];

const CAPTION_KEYWORDS = [
  "describe",
  "caption",
  "what is in",
  "what do you see",
  "tell me about",
  "summarize",
  "summary",
];

function detectIntent(q: string): Intent {
  const lower = q.toLowerCase();
  if (CHANGE_KEYWORDS.some((k) => lower.includes(k))) return "bitemporal";
  if (SAR_KEYWORDS.some((k) => lower.includes(k))) return "optical_sar";
  if (CAPTION_KEYWORDS.some((k) => lower.includes(k))) return "caption";
  return "single_image";
}

const PLANS: Record<Intent, Omit<WorkflowPlan, "intent">> = {
  single_image: {
    intentLabel: "Single-image visual question answering",
    workflow: "VQA_SINGLE",
    understood:
      "You asked a question about a single satellite image. GAIA will accept one image and answer your question based on what it observes.",
    why: "Your query addresses a single observation without comparing across time or sensor modality, so the single-image VQA pipeline is selected.",
    needs: "One satellite image — GeoTIFF, TIFF, PNG or JPEG.",
    next: "After you upload the image, GAIA will run the image through a vision-language model, generate an answer grounded in observed features, and explain its reasoning.",
    requiredInputs: [
      {
        id: "img",
        code: "IMG",
        label: "Satellite image",
        hint: "Upload a GeoTIFF, TIFF, PNG or JPEG satellite image. The backend will answer your question based on this image.",
      },
    ],
    components: [
      {
        name: "Vision encoder",
        role: "Feature extraction",
        note: "Encodes the satellite image into a feature representation suitable for the language model.",
      },
      {
        name: "Language decoder",
        role: "Answer generation",
        note: "Takes the encoded image features together with your question and generates a natural-language answer.",
      },
    ],
  },
  bitemporal: {
    intentLabel: "Bi-temporal change detection",
    workflow: "CHANGE_BITEMPORAL",
    understood:
      "You are asking about changes between two points in time. GAIA needs an earlier and a later image of the same area to compare them.",
    why: "Your query involves temporal comparison — detecting what changed between two observations — so the bi-temporal change detection workflow is selected.",
    needs: "Two co-registered satellite images of the same area taken at different times.",
    next: "After you upload both images, GAIA will align them, detect differences, classify the type of change, and describe the findings with supporting evidence.",
    requiredInputs: [
      {
        id: "t1",
        code: "T1",
        label: "Earlier observation",
        hint: "Upload the satellite image from the earlier date.",
      },
      {
        id: "t2",
        code: "T2",
        label: "Later observation",
        hint: "Upload the satellite image from the later date.",
      },
    ],
    components: [
      {
        name: "Change encoder",
        role: "Bi-temporal feature extraction",
        note: "Processes both images jointly to produce a change-aware feature representation.",
      },
      {
        name: "Change classifier",
        role: "Change type identification",
        note: "Classifies each region as unchanged, newly built, demolished, vegetated, flooded, etc.",
      },
      {
        name: "Language decoder",
        role: "Description generation",
        note: "Produces a natural-language description of the detected changes.",
      },
    ],
  },
  optical_sar: {
    intentLabel: "Optical + SAR fusion analysis",
    workflow: "FUSION_OPT_SAR",
    understood:
      "You are asking a question that benefits from combining optical and radar imagery. GAIA will fuse both modalities for a more complete analysis.",
    why: "Your query references or would benefit from both optical and SAR data, so the optical-SAR fusion pipeline is selected.",
    needs: "One optical image and one SAR image of the same area.",
    next: "After you upload both images, GAIA will align them, fuse the features from both modalities, and generate an analysis that leverages both optical and radar information.",
    requiredInputs: [
      {
        id: "optical",
        code: "OPT",
        label: "Optical image",
        hint: "Upload an optical satellite image (e.g. Sentinel-2, Landsat, Cartosat).",
      },
      {
        id: "sar",
        code: "SAR",
        label: "SAR image",
        hint: "Upload a SAR / radar satellite image (e.g. Sentinel-1, RISAT).",
      },
    ],
    components: [
      {
        name: "Optical encoder",
        role: "Optical feature extraction",
        note: "Encodes the optical image into a feature representation.",
      },
      {
        name: "SAR encoder",
        role: "Radar feature extraction",
        note: "Encodes the SAR image into a feature representation.",
      },
      {
        name: "Fusion module",
        role: "Cross-modal alignment",
        note: "Aligns and merges features from both modalities into a unified representation.",
      },
      {
        name: "Language decoder",
        role: "Answer generation",
        note: "Generates a natural-language answer grounded in the fused features.",
      },
    ],
  },
  caption: {
    intentLabel: "Image captioning and description",
    workflow: "CAPTION_SINGLE",
    understood:
      "You asked GAIA to describe or caption a satellite image. The system will generate a detailed description of the scene.",
    why: "Your query asks for a description rather than a specific question, so the captioning workflow is selected.",
    needs: "One satellite image to describe.",
    next: "After you upload the image, GAIA will generate a detailed, grounded description of the visible features in the scene.",
    requiredInputs: [
      {
        id: "img",
        code: "IMG",
        label: "Satellite image",
        hint: "Upload a GeoTIFF, TIFF, PNG or JPEG satellite image you want described.",
      },
    ],
    components: [
      {
        name: "Vision encoder",
        role: "Feature extraction",
        note: "Encodes the satellite image into a feature representation suitable for the language model.",
      },
      {
        name: "Caption decoder",
        role: "Description generation",
        note: "Generates a rich natural-language description of the scene based on the encoded features.",
      },
    ],
  },
  vqa: {
    intentLabel: "Single-image visual question answering",
    workflow: "VQA_SINGLE",
    understood:
      "You asked a specific question about a satellite image. GAIA will answer based on visual analysis.",
    why: "Your query is a direct question about image content, so the VQA pipeline is selected.",
    needs: "One satellite image.",
    next: "After you upload the image, GAIA will analyze it and answer your question with supporting evidence.",
    requiredInputs: [
      {
        id: "img",
        code: "IMG",
        label: "Satellite image",
        hint: "Upload the satellite image your question refers to.",
      },
    ],
    components: [
      {
        name: "Vision encoder",
        role: "Feature extraction",
        note: "Encodes the satellite image for the language model.",
      },
      {
        name: "Language decoder",
        role: "Answer generation",
        note: "Generates a natural-language answer grounded in observed features.",
      },
    ],
  },
};

export function routeQuery(query: string): WorkflowPlan {
  const intent = detectIntent(query);
  return { intent, ...PLANS[intent] };
}
