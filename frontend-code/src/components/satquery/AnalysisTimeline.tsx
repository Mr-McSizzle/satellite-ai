import { Check, Loader2 } from "lucide-react";
import { STAGES } from "@/lib/satquery/analysis";

export function AnalysisTimeline({ activeIndex }: { activeIndex: number }) {
  return (
    <section className="panel animate-rise p-5">
      <p className="label-mono">Analysis in progress</p>
      <ol className="mt-4 space-y-1">
        {STAGES.map((stage, i) => {
          const done = i < activeIndex;
          const active = i === activeIndex;
          return (
            <li
              key={stage.code}
              className={`flex items-start gap-3 rounded-md px-3 py-2.5 transition-colors ${
                active ? "bg-primary/10" : ""
              }`}
            >
              <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center">
                {done ? (
                  <Check className="size-4 text-success" />
                ) : active ? (
                  <Loader2 className="size-4 animate-spin text-primary" />
                ) : (
                  <span className="size-1.5 rounded-full bg-border" />
                )}
              </span>
              <div className="min-w-0">
                <p
                  className={`font-mono text-xs ${
                    active ? "text-primary" : done ? "text-foreground" : "text-muted-foreground"
                  }`}
                >
                  {stage.code} · {stage.title.toUpperCase()}
                </p>
                {(active || done) && (
                  <p className="mt-0.5 text-sm leading-relaxed text-muted-foreground">{stage.detail}</p>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
