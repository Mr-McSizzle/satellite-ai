import { useRef, useState, type DragEvent } from "react";
import { AlertTriangle, FileImage, Trash2, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { formatBytes } from "@/lib/satquery/file";
import type { ImageModality, RequiredInput, UploadedImage, WorkflowPlan } from "@/lib/satquery/types";

const MODALITIES: { value: ImageModality; label: string }[] = [
  { value: "optical", label: "Optical" },
  { value: "SAR", label: "SAR" },
];

function Slot({
  spec,
  image,
  error,
  onFile,
  onRemove,
  onDate,
  onModality,
  askDate,
}: {
  spec: RequiredInput;
  image: UploadedImage | undefined;
  error: string | undefined;
  onFile: (file: File, modality: ImageModality) => void;
  onRemove: () => void;
  onDate: (value: string) => void;
  onModality: (value: ImageModality) => void;
  askDate: boolean;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);
  const [selectedModality, setSelectedModality] = useState<ImageModality>("optical");
  const modality = image?.modality ?? selectedModality;

  function updateModality(value: ImageModality) {
    setSelectedModality(value);
    onModality(value);
  }

  function drop(e: DragEvent) {
    e.preventDefault();
    setOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) onFile(file, modality);
  }

  return (
    <div className="panel flex flex-col overflow-hidden">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="rounded bg-primary/15 px-2 py-0.5 font-mono text-xs font-semibold text-primary">
            {spec.code}
          </span>
          <span className="text-sm font-medium text-foreground">{spec.label}</span>
        </div>
        {image ? (
          <span className="font-mono text-[11px] text-success">READY</span>
        ) : (
          <span className="font-mono text-[11px] text-muted-foreground">AWAITING</span>
        )}
      </div>

      <div className="flex flex-1 flex-col p-4">
        <p className="mb-3 text-sm leading-relaxed text-muted-foreground">{spec.hint}</p>

        <input
          ref={inputRef}
          type="file"
          accept=".tif,.tiff,.png,.jpg,.jpeg"
          className="sr-only"
          aria-label={`Upload ${spec.label}`}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onFile(file, modality);
            e.target.value = "";
          }}
        />

        <fieldset className="mb-4 rounded-md border border-border bg-surface-raised/60 px-3 py-2">
          <legend className="px-1 label-mono">Modality</legend>
          <div className="flex flex-wrap gap-4">
            {MODALITIES.map((option) => (
              <label
                key={option.value}
                className="flex cursor-pointer items-center gap-2 text-sm text-muted-foreground"
              >
                <input
                  type="radio"
                  name={`modality-${spec.id}`}
                  value={option.value}
                  checked={modality === option.value}
                  onChange={() => updateModality(option.value)}
                  className="accent-primary"
                />
                <span className={modality === option.value ? "text-foreground" : ""}>{option.label}</span>
              </label>
            ))}
          </div>
        </fieldset>

        {!image ? (
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setOver(true);
            }}
            onDragLeave={() => setOver(false)}
            onDrop={drop}
            className={`flex flex-1 flex-col items-center justify-center gap-2 rounded-md border border-dashed px-4 py-10 transition-colors ${
              over ? "border-primary bg-primary/10" : "border-border hover:border-primary/60 hover:bg-surface-raised"
            }`}
          >
            <Upload className="size-6 text-primary" aria-hidden />
            <span className="text-sm text-foreground">Click to select, or drop a file here</span>
            <span className="label-mono">GeoTIFF · TIFF · PNG · JPEG</span>
          </button>
        ) : (
          <div className="space-y-3">
            <div className="relative overflow-hidden rounded-md border border-border bg-surface-raised">
              {image.width > 0 ? (
                <img
                  src={image.previewUrl}
                  alt={`${spec.label} preview`}
                  className="h-48 w-full object-cover"
                />
              ) : (
                <div className="flex h-48 flex-col items-center justify-center gap-2 px-4 text-center">
                  <FileImage className="size-6 text-muted-foreground" aria-hidden />
                  <p className="text-xs text-muted-foreground">
                    File accepted. Browsers cannot render most GeoTIFFs, so no preview is shown —
                    the file itself is still passed to the analysis.
                  </p>
                </div>
              )}
            </div>

            <dl className="grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-[11px] text-muted-foreground">
              <div className="col-span-2 truncate text-foreground">{image.name}</div>
              <div>{formatBytes(image.sizeBytes)}</div>
              <div className="text-right">{image.format}</div>
              <div className="col-span-2">Modality: {image.modality}</div>
              {image.width > 0 && (
                <div className="col-span-2">
                  {image.width} × {image.height} px
                </div>
              )}
            </dl>

            {!image.mayCarryGeoMetadata && (
              <p className="text-xs leading-relaxed text-muted-foreground">
                PNG/JPEG previews are supported in the browser. The backend still needs upload
                support that stores or converts the file and returns an analysis reference.
              </p>
            )}

            {askDate && (
              <label className="block">
                <span className="label-mono">Observation date (optional, entered by you)</span>
                <input
                  type="date"
                  value={image.observationDate ?? ""}
                  onChange={(e) => onDate(e.target.value)}
                  className="mt-1 w-full rounded-md border border-input bg-surface-raised px-3 py-2 font-mono text-sm text-foreground outline-none focus:border-primary"
                />
              </label>
            )}

            <div className="flex gap-2">
              <Button variant="secondary" size="sm" onClick={() => inputRef.current?.click()}>
                Replace
              </Button>
              <Button variant="ghost" size="sm" onClick={onRemove} className="gap-1.5 text-muted-foreground">
                <Trash2 className="size-3.5" /> Remove
              </Button>
            </div>
          </div>
        )}

        {error && (
          <p className="mt-3 flex items-start gap-2 text-xs leading-relaxed text-destructive">
            <AlertTriangle className="mt-0.5 size-3.5 shrink-0" /> {error}
          </p>
        )}
      </div>
    </div>
  );
}

export function ImageryUpload({
  plan,
  images,
  errors,
  onFile,
  onRemove,
  onDate,
  onModality,
}: {
  plan: WorkflowPlan;
  images: UploadedImage[];
  errors: Record<string, string | undefined>;
  onFile: (slot: RequiredInput["id"], file: File, modality: ImageModality) => void;
  onRemove: (slot: RequiredInput["id"]) => void;
  onDate: (slot: RequiredInput["id"], value: string) => void;
  onModality: (slot: RequiredInput["id"], value: ImageModality) => void;
}) {
  return (
    <section className="animate-rise space-y-4">
      <div className="flex items-baseline justify-between">
        <h2 className="text-lg font-semibold tracking-tight text-foreground">Required imagery</h2>
        <span className="label-mono">
          {images.length}/{plan.requiredInputs.length} supplied
        </span>
      </div>
      <div className={`grid gap-4 ${plan.requiredInputs.length > 1 ? "md:grid-cols-2" : ""}`}>
        {plan.requiredInputs.map((spec) => (
          <Slot
            key={spec.id}
            spec={spec}
            image={images.find((i) => i.slot === spec.id)}
            error={errors[spec.id]}
            onFile={(f, modality) => onFile(spec.id, f, modality)}
            onRemove={() => onRemove(spec.id)}
            onDate={(v) => onDate(spec.id, v)}
            onModality={(v) => onModality(spec.id, v)}
            askDate={plan.intent === "bitemporal"}
          />
        ))}
      </div>
    </section>
  );
}
