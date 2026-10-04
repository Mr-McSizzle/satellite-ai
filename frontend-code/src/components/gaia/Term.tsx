import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

const GLOSSARY: Record<string, string> = {
  VQA: "Visual Question Answering — answering a natural-language question about the content of an image.",
  SAR: "Synthetic Aperture Radar — radar-based Earth observation. It works through cloud and darkness, and water appears very dark because it reflects the signal away.",
  Optical:
    "Satellite imagery formed from reflected sunlight, close to what the eye would see. Cloud cover blocks it.",
  "Bi-temporal":
    "Two observations of the same geographic area acquired at different times, compared against each other.",
  "RS-VLM":
    "Remote-Sensing Vision-Language Model — a vision-language model specialised on satellite imagery, so it connects image content to the wording of a question.",
  "Prithvi-EO-2.0":
    "A remote-sensing foundation model used here as an Earth Observation perception component: it converts imagery into visual representations for downstream reasoning.",
  Grounding:
    "Locating the specific image region that a phrase in your question refers to, instead of only answering in words.",
  GeoTIFF:
    "A TIFF image that can carry geospatial metadata such as coordinates, projection and sometimes acquisition details.",
  "Co-registered":
    "Two images aligned so that the same pixel position corresponds to the same point on the ground.",
};

export function Term({ children }: { children: string }) {
  const definition = GLOSSARY[children];
  if (!definition) return <>{children}</>;
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span className="cursor-help border-b border-dashed border-primary/60 text-foreground">
          {children}
        </span>
      </TooltipTrigger>
      <TooltipContent className="max-w-xs text-xs leading-relaxed">{definition}</TooltipContent>
    </Tooltip>
  );
}
