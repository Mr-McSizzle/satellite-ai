import { useState } from "react";
import { Check, ChevronDown, ImageOff, Sparkles, X } from "lucide-react";
import type { ReactNode } from "react";
import type { AnalysisResult, UploadedImage, WorkflowPlan } from "@/lib/satquery/types";
import { CompareSlider } from "./CompareSlider";

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "None";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return JSON.stringify(value, null, 2);
}

function toolName(tool: unknown): string {
  if (typeof tool === "string") return tool;
  if (tool && typeof tool === "object") {
    const maybeName = "name" in tool ? tool.name : "tool" in tool ? tool.tool : undefined;
    if (typeof maybeName === "string") return maybeName;
  }
  return formatValue(tool);
}

function StatusLine({ ok, children }: { ok: boolean; children: ReactNode }) {
  return (
    <li className="flex gap-2 text-sm leading-relaxed text-muted-foreground">
      {ok ? (
        <Check className="mt-0.5 size-4 shrink-0 text-success" />
      ) : (
        <X className="mt-0.5 size-4 shrink-0 text-destructive" />
      )}
      <span>{children}</span>
    </li>
  );
}

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
          <p className="label-mono">GAIA RESULT</p>
          <span className="rounded-full border border-success/40 bg-success/10 px-2.5 py-0.5 font-mono text-[10px] tracking-wider text-success">
            BACKEND
          </span>
        </div>
        <div className="px-5 py-6">
          <p className="mb-3 font-mono text-xs text-muted-foreground">
            Task: <span className="text-primary">{result.task}</span>
          </p>
          <div className="flex gap-3">
            <Sparkles className="mt-1 size-5 shrink-0 text-primary" aria-hidden />
            <p className="text-xl leading-relaxed font-medium tracking-tight text-foreground">
              {result.answer}
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <div className="panel p-5 lg:col-span-3">
          <p className="label-mono">Answer</p>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{result.meaning}</p>
        </div>
        <div className="panel p-5 lg:col-span-2">
          <p className="label-mono">Backend summary</p>
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
          {result.displayEvidence.map((ev) => {
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
        <p className="label-mono">Evidence</p>
        {result.evidence.length ? (
          <div className="mt-3 grid gap-3">
            {result.evidence.map((item, index) => (
              <div key={`${item.type}-${index}`} className="rounded-md border border-border bg-surface-raised p-3">
                <p className="font-mono text-xs text-primary">{item.type}</p>
                <pre className="mt-2 overflow-auto whitespace-pre-wrap text-xs leading-relaxed text-muted-foreground">
                  {formatValue(item.data)}
                </pre>
              </div>
            ))}
          </div>
        ) : (
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            The backend did not return evidence items for this response.
          </p>
        )}
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

      <div className="panel p-5">
        <p className="label-mono">Execution trace</p>
        <div className="mt-3 grid gap-4 md:grid-cols-2">
          <div>
            <p className="font-mono text-xs text-muted-foreground">Classifier</p>
            <p className="mt-1 text-sm text-foreground">
              {result.execution_trace.task_selected || result.task}
            </p>
          </div>
          <div>
            <p className="font-mono text-xs text-muted-foreground">Execution status</p>
            <p className="mt-1 text-sm text-foreground">
              {result.execution_trace.execution_status || result.status}
            </p>
          </div>
          <div className="md:col-span-2">
            <p className="font-mono text-xs text-muted-foreground">Tools</p>
            {result.execution_trace.tools_invoked.length ? (
              <ul className="mt-2 space-y-1">
                {result.execution_trace.tools_invoked.map((tool, index) => (
                  <StatusLine key={`${toolName(tool)}-${index}`} ok>
                    {toolName(tool)}
                  </StatusLine>
                ))}
              </ul>
            ) : (
              <p className="mt-1 text-sm text-muted-foreground">No tools reported by backend.</p>
            )}
          </div>
          <div>
            <p className="font-mono text-xs text-muted-foreground">Warnings</p>
            {result.execution_trace.warnings.length ? (
              <ul className="mt-2 space-y-1">
                {result.execution_trace.warnings.map((warning, index) => (
                  <StatusLine key={`warning-${index}`} ok={false}>
                    {formatValue(warning)}
                  </StatusLine>
                ))}
              </ul>
            ) : (
              <p className="mt-1 text-sm text-muted-foreground">None</p>
            )}
          </div>
          <div>
            <p className="font-mono text-xs text-muted-foreground">Errors</p>
            {result.execution_trace.errors.length ? (
              <ul className="mt-2 space-y-1">
                {result.execution_trace.errors.map((error, index) => (
                  <StatusLine key={`error-${index}`} ok={false}>
                    {formatValue(error)}
                  </StatusLine>
                ))}
              </ul>
            ) : (
              <p className="mt-1 text-sm text-muted-foreground">None</p>
            )}
          </div>
          <div className="md:col-span-2">
            <p className="font-mono text-xs text-muted-foreground">Audit</p>
            <pre className="mt-2 overflow-auto whitespace-pre-wrap rounded-md border border-border bg-surface-raised p-3 text-xs leading-relaxed text-muted-foreground">
              {formatValue(result.execution_trace.validation_result)}
            </pre>
          </div>
        </div>
      </div>

      <div className="panel overflow-hidden">
        <button
          type="button"
          onClick={() => setTraceOpen((o) => !o)}
          aria-expanded={traceOpen}
          className="flex w-full items-center justify-between px-5 py-4"
        >
          <span className="label-mono">Trace steps</span>
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
