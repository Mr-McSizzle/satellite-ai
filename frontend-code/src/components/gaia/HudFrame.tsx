import type { ReactNode } from "react";

/** Decorative FUI corner brackets around any block. */
export function HudFrame({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`relative ${className}`}>
      <span className="pointer-events-none absolute -left-1 -top-1 size-4 border-l border-t border-primary/50" />
      <span className="pointer-events-none absolute -right-1 -top-1 size-4 border-r border-t border-primary/50" />
      <span className="pointer-events-none absolute -bottom-1 -left-1 size-4 border-b border-l border-primary/50" />
      <span className="pointer-events-none absolute -bottom-1 -right-1 size-4 border-b border-r border-primary/50" />
      {children}
    </div>
  );
}
