import { useState } from "react";
import { ChevronDown, ImageOff, Sparkles } from "lucide-react";
import type { AnalysisResult, UploadedImage, WorkflowPlan } from "@/lib/satquery/types";
import { CompareSlider } from "./CompareSlider";

export function ResultDashboard({
  result,
  plan,
  images,
}: {
  result: AnalysisResult;
  plan: WorkflowPlan;
  images: UploadedImage[];
}) {
  const [traceOpen, setTraceOpen] = useState(false);
  const img = (slot?: string) => images.find((i) => i.slot === slot);
  const pairA = img(plan.intent === "bitemporal" ? "t1" : "optical");
  const pairB = img(plan.intent === "bitemporal" ? "t2" : "sar");
  const showSlider =
    (plan.intent === "bitemporal" || plan.intent === "optical_sar") &&
    !!pairA?.width &&
    !!pairB?.width;

  return (
    <section className="animate-rise space-y-4">
      <div className="panel overflow-hidden">
        <div className="flex items-center justify-between border-b border-border px-5 py-3">
          <p className="label-mono">AI intelligence finding</p>
          <span className="rounded-full border border-warning/40 bg-warning/10 px-2.5 py-0.5 font-mono text-[10px] tracking-wider text-warning">
            DEMO DATA
          </span>
        </div>
        <div className="px-5 py-6">
          <div className="flex gap-3">
            <Sparkles className="mt-1 size-5 shrink-0 text-primary" aria-hidden />
            <p className="text-xl leading-relaxed font-medium tracking-tight text-foreground">
              {result.finding}
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <div className="panel p-5 lg:col-span-3">
          <p className="label-mono">What this means</p>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{result.meaning}</p>
        </div>
        <div className="panel p-5 lg:col-span-2">
          <p className="label-mono">Structured observations</p>
          <ul className="mt-3 space-y-2">
            {result.observations.map((o) => (
              <li key={o} className="flex gap-2 text-sm leading-relaxed text-muted-foreground">
                <span className="mt-2 size-1 shrink-0 rounded-full bg-primary" />
                <span>{o}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="panel p-5">
        <p className="label-mono">Visual evidence</p>
        {showSlider && pairA && pairB && (
          <div className="mt-4">
            <CompareSlider
              before={pairA.previewUrl}
              after={pairB.previewUrl}
              beforeLabel={plan.requiredInputs[0]?.code ?? "A"}
              afterLabel={plan.requiredInputs[1]?.code ?? "B"}
            />
          </div>
        )}
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {result.evidence.map((ev) => {
            const source = img(ev.slot);
            return (
              <figure key={ev.id} className="overflow-hidden rounded-md border border-border bg-surface-raised">
                {source?.width ? (
                  <img src={source.previewUrl} alt={ev.caption} className="h-44 w-full object-cover" />
                ) : (
                  <div className="flex h-44 flex-col items-center justify-center gap-2 px-4 text-center">
                    <ImageOff className="size-5 text-muted-foreground" aria-hidden />
                    <p className="text-xs leading-relaxed text-muted-foreground">
                      {ev.note ?? "No renderable preview for this input."}
                    </p>
                  </div>
                )}
                <figcaption className="border-t border-border px-3 py-2 font-mono text-[11px] text-muted-foreground">
                  {ev.caption}
                </figcaption>
              </figure>
            );
          })}
        </div>
      </div>

      <div className="panel p-5">
        <p className="label-mono">Confidence</p>
        {result.confidence ? (
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            {Math.round(result.confidence.value * 100)}% — {result.confidence.explanation}
          </p>
        ) : (
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            No confidence score is shown, because no scoring model produced one for this request. A
            number here would be invented rather than measured. When a real analysis backend is
            connected, its score appears in this panel together with a plain-language reading of
            what the score does and does not guarantee.
          </p>
        )}
      </div>

      <div className="panel overflow-hidden">
        <button
          type="button"
          onClick={() => setTraceOpen((o) => !o)}
          aria-expanded={traceOpen}
          className="flex w-full items-center justify-between px-5 py-4"
        >
          <span className="label-mono">Execution trace</span>
          <ChevronDown className={`size-4 text-muted-foreground transition-transform ${traceOpen ? "rotate-180" : ""}`} />
        </button>
        {traceOpen && (
          <ol className="animate-rise border-t border-border px-5 py-4">
            {result.executionTrace.map((s) => (
              <li key={s.code} className="flex gap-4 border-l border-border py-3 pl-4 first:pt-0 last:pb-0">
                <span className="font-mono text-xs text-primary">{s.code}</span>
                <div>
                  <p className="text-sm font-medium text-foreground">{s.title}</p>
                  <p className="mt-0.5 text-sm leading-relaxed text-muted-foreground">{s.detail}</p>
                </div>
              </li>
            ))}
            <li className="pt-3 text-xs leading-relaxed text-muted-foreground">
              This is an auditable summary of observable workflow stages, not internal model
              reasoning.
            </li>
          </ol>
        )}
      </div>
    </section>
  );
}
