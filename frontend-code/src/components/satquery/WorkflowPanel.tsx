import { Brain, Compass, Layers, ListChecks } from "lucide-react";
import type { WorkflowPlan } from "@/lib/satquery/types";
import { Term } from "./Term";

const BLOCKS = [
  { key: "understood", icon: Compass, title: "What I understood" },
  { key: "why", icon: Brain, title: "Why this workflow" },
  { key: "needs", icon: Layers, title: "What I need from you" },
  { key: "next", icon: ListChecks, title: "What happens next" },
] as const;

export function WorkflowPanel({ plan }: { plan: WorkflowPlan }) {
  return (
    <section className="animate-rise space-y-4">
      <div className="panel overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-5 py-4">
          <div>
            <p className="label-mono text-primary/80">Query understood</p>
            <h2 className="mt-1 text-xl font-semibold tracking-tight text-foreground">
              {plan.intentLabel}
            </h2>
          </div>
          <span className="font-mono text-[10px] tracking-[0.2em] text-warning uppercase">
            UI hint only
          </span>
        </div>

        <div className="grid gap-px bg-border sm:grid-cols-2">
          {BLOCKS.map(({ key, icon: Icon, title }) => (
            <div key={key} className="bg-surface p-5">
              <div className="flex items-center gap-2">
                <Icon className="size-4 text-primary" aria-hidden />
                <h3 className="label-mono !text-foreground">{title}</h3>
              </div>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{plan[key]}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="panel p-5">
        <p className="label-mono text-primary/80">Upload guidance</p>
        <div className="mt-4 grid gap-5 sm:grid-cols-2">
          <div className="space-y-3 border-r border-border/60 pr-0 sm:pr-5">
            <div>
              <p className="text-sm text-muted-foreground">Selected workflow</p>
              <p className="mt-1 font-mono text-sm text-primary">{plan.workflow}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Required imagery</p>
              <ul className="mt-2 space-y-1.5">
                {plan.requiredInputs.map((r) => (
                  <li key={r.id} className="font-mono text-sm text-foreground">
                    <span className="text-primary">{r.code}</span> — {r.label}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="space-y-3">
            {plan.components.map((c) => (
              <div key={c.name} className="border border-border bg-surface-raised p-3">
                <p className="font-mono text-sm text-foreground">
                  <Term>{c.name}</Term>
                </p>
                <p className="label-mono mt-0.5">{c.role}</p>
                <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{c.note}</p>
              </div>
            ))}
            <p className="text-xs leading-relaxed text-muted-foreground">
              These components are frontend guidance for the upload shape. The backend selects the
              actual task, routes tools, executes models and returns the measured result.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
