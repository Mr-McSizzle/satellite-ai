import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { CheckCircle2, Circle, Satellite } from "lucide-react";
import { Button } from "@/components/ui/button";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryConsole } from "@/components/satquery/QueryConsole";
import { WorkflowPanel } from "@/components/satquery/WorkflowPanel";
import { ImageryUpload } from "@/components/satquery/ImageryUpload";
import { AnalysisTimeline } from "@/components/satquery/AnalysisTimeline";
import { ResultDashboard } from "@/components/satquery/ResultDashboard";
import { EvaluationSection } from "@/components/satquery/EvaluationSection";
import { EarthGlobe } from "@/components/satquery/EarthGlobe";
import { HudFrame } from "@/components/satquery/HudFrame";
import { routeQuery } from "@/lib/satquery/router";
import { readImageFile } from "@/lib/satquery/file";
import { STAGES, runDemoAnalysis } from "@/lib/satquery/analysis";
import type { AnalysisResult, SlotId, UploadedImage, WorkflowPlan } from "@/lib/satquery/types";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "GAIA — Understand Earth. Ask GAIA." },
      {
        name: "description",
        content:
          "Ask questions about satellite imagery in natural language. GAIA understands your intent, determines the appropriate remote-sensing workflow, requests only the imagery required, and returns evidence-grounded insights.",
      },
      { property: "og:title", content: "GAIA — Understand Earth. Ask GAIA." },
      {
        property: "og:description",
        content:
          "An agentic remote-sensing intelligence system that translates natural-language questions into specialised Earth observation analysis workflows.",
      },
    ],
  }),
  component: SatQuery,
});

function StatusDot({ label, ok }: { label: string; ok: boolean }) {
  return (
    <span className="flex items-center gap-1.5 font-mono text-[11px] text-muted-foreground">
      <span
        className={`size-1.5 rounded-full ${ok ? "animate-pulse-dot bg-success" : "bg-muted-foreground"}`}
      />
      {label}
    </span>
  );
}

function SatQuery() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [plan, setPlan] = useState<WorkflowPlan | null>(null);
  const [images, setImages] = useState<UploadedImage[]>([]);
  const [errors, setErrors] = useState<Record<string, string | undefined>>({});
  const [stage, setStage] = useState(-1);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const planRef = useRef<HTMLDivElement>(null);

  const handleSubmit = useCallback((q: string) => {
    const next = routeQuery(q);
    setSubmittedQuery(q);
    setPlan(next);
    setImages([]);
    setErrors({});
    setResult(null);
    setStage(-1);
  }, []);

  useEffect(() => {
    if (plan) planRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [plan]);

  const onFile = useCallback(async (slot: SlotId, file: File) => {
    try {
      const parsed = await readImageFile(slot, file);
      setImages((prev) => {
        const old = prev.find((i) => i.slot === slot);
        if (old) URL.revokeObjectURL(old.previewUrl);
        return [...prev.filter((i) => i.slot !== slot), parsed];
      });
      setErrors((e) => ({ ...e, [slot]: undefined }));
    } catch (err) {
      setErrors((e) => ({ ...e, [slot]: err instanceof Error ? err.message : "Could not read file." }));
    }
  }, []);

  const onRemove = useCallback((slot: SlotId) => {
    setImages((prev) => {
      const old = prev.find((i) => i.slot === slot);
      if (old) URL.revokeObjectURL(old.previewUrl);
      return prev.filter((i) => i.slot !== slot);
    });
    setResult(null);
    setStage(-1);
  }, []);

  const onDate = useCallback((slot: SlotId, value: string) => {
    setImages((prev) => prev.map((i) => (i.slot === slot ? { ...i, observationDate: value } : i)));
  }, []);

  const checks = useMemo(() => {
    if (!plan) return [];
    const supplied = images.length === plan.requiredInputs.length;
    const readable = images.every((i) => i.width > 0 || i.mayCarryGeoMetadata);
    return [
      { label: "Query understood", ok: true },
      { label: `Required inputs supplied (${images.length}/${plan.requiredInputs.length})`, ok: supplied },
      { label: "Images readable", ok: supplied && readable },
      {
        label:
          plan.intent === "bitemporal"
            ? "Earlier and later observations identified"
            : plan.intent === "optical_sar"
              ? "Optical and radar observations identified"
              : "Input configuration valid",
        ok: supplied,
      },
    ];
  }, [plan, images]);

  const ready = checks.length > 0 && checks.every((c) => c.ok);
  const running = stage >= 0 && stage < STAGES.length;

  useEffect(() => {
    if (!running) return;
    const t = setTimeout(() => setStage((s) => s + 1), 420);
    return () => clearTimeout(t);
  }, [running, stage]);

  useEffect(() => {
    if (stage === STAGES.length && plan && !result) {
      setResult(runDemoAnalysis(submittedQuery, plan, images));
    }
  }, [stage, plan, result, submittedQuery, images]);

  return (
    <TooltipProvider delayDuration={150}>
      <div className="min-h-screen">
        <header className="sticky top-0 z-20 border-b border-border bg-background/80 backdrop-blur">
          <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-5 py-3">
            <div className="flex items-center gap-2.5">
              <Satellite className="size-5 text-primary" aria-hidden />
              <div className="leading-none">
                <div className="font-mono text-sm font-semibold tracking-[0.18em] text-foreground">
                  GAIA
                </div>
                <div className="mt-1 font-mono text-[9px] tracking-[0.24em] text-muted-foreground uppercase">
                  Earth Observation Intelligence
                </div>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <StatusDot label="SYSTEM READY" ok />
              <StatusDot label="AGENT READY" ok />
              <StatusDot label="MODEL BACKEND — NOT CONNECTED" ok={false} />
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-6xl space-y-12 px-5 py-12 sm:py-16">
          <section className="grid items-center gap-8 lg:grid-cols-[1.05fr_0.95fr]">
            <div className="max-w-xl">
              <p className="label-mono text-primary/80">AGENTIC EARTH OBSERVATION INTELLIGENCE</p>
              <h1 className="mt-4 text-4xl leading-[1.05] font-semibold tracking-[-0.04em] text-balance text-foreground sm:text-5xl">
                Understand Earth.
                <br />
                Ask GAIA.
              </h1>
              <p className="mt-5 max-w-lg text-base leading-relaxed text-muted-foreground">
                Ask questions about satellite imagery in natural language. GAIA determines the right
                analysis, requests the imagery it needs, and explains the evidence behind the result.
              </p>

              <div className="mt-6 flex flex-wrap items-center gap-2 text-[10px] font-mono tracking-[0.18em] text-muted-foreground uppercase">
                <span className="text-primary">NATURAL LANGUAGE</span>
                <span className="text-muted-foreground/60">•</span>
                <span>AUTOMATIC ROUTING</span>
                <span className="text-muted-foreground/60">•</span>
                <span>QUERY-DRIVEN IMAGERY</span>
              </div>
            </div>

            <div className="relative">
              <HudFrame className="p-6">
                <EarthGlobe active={running} />
              </HudFrame>
              <div className="mt-4 flex items-center justify-center gap-2 font-mono text-[10px] tracking-[0.22em] text-muted-foreground uppercase">
                <span className="inline-block size-2 rounded-full bg-success shadow-[0_0_12px_rgba(132,214,164,0.8)]" />
                <span>{running ? "GAIA SCANNING" : "GAIA READY FOR QUERY"}</span>
              </div>
            </div>
          </section>

          <QueryConsole value={query} onChange={setQuery} onSubmit={handleSubmit} busy={running} />


          <div ref={planRef} className="space-y-12 scroll-mt-20">
            {plan && (
              <>
                <WorkflowPanel plan={plan} />

                <ImageryUpload
                  plan={plan}
                  images={images}
                  errors={errors}
                  onFile={onFile}
                  onRemove={onRemove}
                  onDate={onDate}
                />

                <section className="panel animate-rise p-5">
                  <p className="label-mono">Readiness</p>
                  <ul className="mt-3 grid gap-2 sm:grid-cols-2">
                    {checks.map((c) => (
                      <li key={c.label} className="flex items-center gap-2 text-sm">
                        {c.ok ? (
                          <CheckCircle2 className="size-4 shrink-0 text-success" />
                        ) : (
                          <Circle className="size-4 shrink-0 text-muted-foreground" />
                        )}
                        <span className={c.ok ? "text-foreground" : "text-muted-foreground"}>{c.label}</span>
                      </li>
                    ))}
                  </ul>
                  <Button
                    className="mt-5 w-full sm:w-auto"
                    disabled={!ready || running}
                    onClick={() => {
                      setResult(null);
                      setStage(0);
                    }}
                  >
                    {running ? "Analyzing…" : "Analyze with GAIA"}
                  </Button>
                </section>

                {stage >= 0 && !result && <AnalysisTimeline activeIndex={stage} />}
                {result && <ResultDashboard result={result} plan={plan} images={images} />}
              </>
            )}
          </div>

          <EvaluationSection />

          <footer className="border-t border-border pt-6 text-xs leading-relaxed text-muted-foreground">
            GAIA prototype. Workflow routing runs locally from the wording of your query and is
            labelled as demo routing. No remote-sensing model is executed in this build, so no
            sensor metadata, acquisition date, coordinate, area measurement or confidence value is
            reported unless it comes from the file you supplied or from you directly.
          </footer>
        </main>
      </div>
    </TooltipProvider>
  );
}
