import earthTexture from "@/assets/earth-texture.jpg";

/**
 * Presentational FUI globe: an equirectangular texture scrolled behind a
 * spherical mask, wrapped in orbit rings and HUD telemetry. No data logic.
 */
export function EarthGlobe({ active }: { active?: boolean }) {
  return (
    <div className="relative mx-auto aspect-square w-full max-w-[26rem]">
      {/* orbit rings */}
      <div className="pointer-events-none absolute inset-0 animate-[orbit-spin_28s_linear_infinite] rounded-full border border-primary/25" />
      <div className="pointer-events-none absolute inset-[-8%] animate-[orbit-spin_44s_linear_infinite_reverse] rounded-full border border-dashed border-primary/20" />
      <div
        className="pointer-events-none absolute inset-[6%] rounded-full border border-primary/15"
        style={{ transform: "rotateX(74deg)" }}
      />
      <div
        className="pointer-events-none absolute inset-[6%] rounded-full border border-primary/10"
        style={{ transform: "rotateX(74deg) rotateY(48deg)" }}
      />

      {/* satellite pip riding the outer ring */}
      <div className="pointer-events-none absolute inset-[-8%] animate-[orbit-spin_16s_linear_infinite]">
        <span className="absolute left-1/2 top-0 size-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary shadow-[0_0_12px_4px_var(--glow)]" />
      </div>

      {/* sphere */}
      <div className="absolute inset-[10%] overflow-hidden rounded-full shadow-[0_0_80px_-10px_var(--glow)]">
        <div
          className="size-full animate-[globe-spin_38s_linear_infinite] bg-repeat-x"
          style={{
            backgroundImage: `url(${earthTexture})`,
            backgroundSize: "200% 100%",
          }}
        />
        {/* meridian grid */}
        <div className="pointer-events-none absolute inset-0 opacity-40 [background-image:linear-gradient(var(--grid-line)_1px,transparent_1px),linear-gradient(90deg,var(--grid-line)_1px,transparent_1px)] [background-size:100%_14%,10%_100%]" />
        {/* spherical shading + terminator */}
        <div className="pointer-events-none absolute inset-0 rounded-full [background:radial-gradient(circle_at_32%_28%,transparent_0%,transparent_38%,oklch(0.12_0.03_250/0.72)_82%,oklch(0.1_0.03_250/0.92)_100%)]" />
        <div className="pointer-events-none absolute inset-0 rounded-full [background:radial-gradient(circle_at_30%_25%,var(--glow),transparent_58%)]" />
        {/* scan sweep */}
        {active && (
          <div className="pointer-events-none absolute inset-x-0 h-1/3 animate-[globe-scan_2.4s_ease-in-out_infinite] [background:linear-gradient(180deg,transparent,var(--glow),transparent)]" />
        )}
      </div>

      {/* atmosphere */}
      <div className="pointer-events-none absolute inset-[8%] rounded-full ring-1 ring-primary/30 [box-shadow:inset_0_0_40px_-8px_var(--glow)]" />

      {/* HUD ticks */}
      <div className="pointer-events-none absolute -left-2 top-1/2 -translate-y-1/2 font-mono text-[10px] tracking-[0.2em] text-muted-foreground">
        LAT
      </div>
      <div className="pointer-events-none absolute -right-1 top-1/2 -translate-y-1/2 font-mono text-[10px] tracking-[0.2em] text-muted-foreground">
        LON
      </div>
    </div>
  );
}
