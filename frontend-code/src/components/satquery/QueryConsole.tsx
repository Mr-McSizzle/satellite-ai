import { useState, type FormEvent } from "react";
import { ArrowRight, Radar } from "lucide-react";
import { Button } from "@/components/ui/button";

const EXAMPLES = [
  "Describe the land-cover in this image.",
  "What changed between these two dates?",
  "Highlight the water body.",
  "Has the built-up area increased?",
  "Identify flooded areas using optical and SAR imagery.",
  "Are there roads near the settlement?",
];

export function QueryConsole({
  value,
  onChange,
  onSubmit,
  busy,
}: {
  value: string;
  onChange: (v: string) => void;
  onSubmit: (q: string) => void;
  busy?: boolean;
}) {
  const [focused, setFocused] = useState(false);

  function submit(e: FormEvent) {
    e.preventDefault();
    if (value.trim().length > 2) onSubmit(value);
  }

  return (
    <section className="animate-rise">
      <div className="mb-3 flex items-center justify-between gap-3">
        <p className="label-mono text-primary/80">Query interface</p>
        <span className="font-mono text-[10px] tracking-[0.2em] text-muted-foreground uppercase">
          Tell GAIA what you want to know
        </span>
      </div>

      <form onSubmit={submit}>
        <div
          className={`relative overflow-hidden border border-border bg-surface/80 p-2 transition-all ${
            focused
              ? "border-primary/60 shadow-[0_0_0_1px_var(--ring),0_18px_60px_-20px_var(--glow)]"
              : "shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]"
          }`}
        >
          <div className="flex items-start gap-3 p-3">
            <div className="mt-2 flex size-9 items-center justify-center rounded-md border border-primary/30 bg-primary/5">
              <Radar className="size-4 shrink-0 text-primary" aria-hidden />
            </div>
            <textarea
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) submit(e);
              }}
              rows={2}
              aria-label="Your question about the imagery"
              placeholder="Ask GAIA about the imagery, change, land cover, flooding, or water body..."
              className="min-h-16 flex-1 resize-none bg-transparent text-base leading-relaxed text-foreground outline-none placeholder:text-muted-foreground"
            />
            <Button
              type="submit"
              disabled={busy || value.trim().length < 3}
              className="mt-1 gap-2 rounded-md px-4 py-2 text-[11px] tracking-[0.18em] uppercase"
            >
              Ask GAIA <ArrowRight className="size-4" />
            </Button>
          </div>
        </div>
      </form>

      <div className="mt-4 flex flex-wrap gap-2">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            type="button"
            onClick={() => {
              onChange(ex);
              onSubmit(ex);
            }}
            className="border border-border bg-transparent px-3 py-1.5 text-[10px] tracking-[0.14em] text-muted-foreground uppercase transition-colors hover:border-primary/50 hover:text-foreground"
          >
            {ex}
          </button>
        ))}
      </div>
    </section>
  );
}
