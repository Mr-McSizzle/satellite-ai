import { useRef, useState } from "react";

export function CompareSlider({
  before,
  after,
  beforeLabel,
  afterLabel,
}: {
  before: string;
  after: string;
  beforeLabel: string;
  afterLabel: string;
}) {
  const [pos, setPos] = useState(50);
  const ref = useRef<HTMLDivElement>(null);

  return (
    <div className="space-y-2">
      <div
        ref={ref}
        className="relative aspect-video w-full select-none overflow-hidden rounded-md border border-border bg-surface-raised"
      >
        <img src={after} alt={afterLabel} className="absolute inset-0 size-full object-cover" />
        <div className="absolute inset-0 overflow-hidden" style={{ width: `${pos}%` }}>
          <img
            src={before}
            alt={beforeLabel}
            className="absolute inset-0 h-full object-cover"
            style={{ width: ref.current?.clientWidth ?? "100%" }}
          />
        </div>
        <div className="pointer-events-none absolute inset-y-0 w-px bg-primary" style={{ left: `${pos}%` }} />
        <span className="pointer-events-none absolute left-3 top-3 rounded bg-background/80 px-2 py-1 font-mono text-[11px] text-foreground">
          {beforeLabel}
        </span>
        <span className="pointer-events-none absolute right-3 top-3 rounded bg-background/80 px-2 py-1 font-mono text-[11px] text-foreground">
          {afterLabel}
        </span>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        value={pos}
        aria-label="Comparison position"
        onChange={(e) => setPos(Number(e.target.value))}
        className="w-full accent-[var(--primary)]"
      />
    </div>
  );
}
