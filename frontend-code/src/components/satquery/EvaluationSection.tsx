import { ChevronDown } from "lucide-react";
import { useState } from "react";

const ROWS = [
  { task: "Single-image VQA", eval: "RSVQA-style question/answer benchmarks" },
  { task: "Captioning & grounding", eval: "VRSBench description and referring-expression splits" },
  { task: "Bi-temporal change analysis", eval: "CDVQA and co-registered bi-temporal pairs" },
  { task: "Optical + SAR", eval: "Co-registered Cartosat / RISAT imagery where available" },
  { task: "Agentic orchestration", eval: "Auditable execution trace and correctness of workflow routing" },
];

export function EvaluationSection() {
  const [open, setOpen] = useState(false);
  return (
    <section className="panel overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between px-5 py-4 text-left"
        aria-expanded={open}
      >
        <span className="label-mono">ISRO / SAC evaluation alignment</span>
        <ChevronDown className={`size-4 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`} />
      </button>
      {open && (
        <div className="animate-rise border-t border-border px-5 py-4">
          <p className="mb-4 max-w-3xl text-sm leading-relaxed text-muted-foreground">
            The workflows this prototype routes between map onto the evaluation tracks used for
            remote-sensing language tasks. The table lists the benchmark family each track would be
            measured against; it records intent, not results already obtained.
          </p>
          <dl className="grid gap-px overflow-hidden rounded-md border border-border bg-border sm:grid-cols-2">
            {ROWS.map((r) => (
              <div key={r.task} className="bg-surface p-4">
                <dt className="text-sm font-medium text-foreground">{r.task}</dt>
                <dd className="mt-1 font-mono text-xs leading-relaxed text-muted-foreground">{r.eval}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </section>
  );
}
