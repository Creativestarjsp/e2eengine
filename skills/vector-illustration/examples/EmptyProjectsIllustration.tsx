import * as React from "react";

export interface EmptyProjectsIllustrationProps {
  /** Folder front. Pass the design system's primary colour or a CSS variable. */
  primaryColor?: string;
  /** Folder back. A deeper shade of the primary. */
  secondaryColor?: string;
  /** Loose pages behind the folder. Use a darker tint in dark mode. */
  tintColor?: string;
  /** Sheets and the badge ring. */
  surfaceColor?: string;
  /** The add badge and the ground shadow. */
  contrastColor?: string;
  className?: string;
  width?: number | string;
  height?: number | string;
  /** Set only when the artwork carries meaning. Without it the artwork is decorative and hidden from assistive technology. */
  title?: string;
}

export function EmptyProjectsIllustration({
  primaryColor = "#6366F1",
  secondaryColor = "#4F46E5",
  tintColor = "#E0E7FF",
  surfaceColor = "#FFFFFF",
  contrastColor = "#1F2937",
  className,
  width = "100%",
  height,
  title,
}: EmptyProjectsIllustrationProps) {
  // Colours go through `style` so callers can pass CSS variables.
  const fill = (color: string) => ({ fill: color });
  const accessibility = title ? { role: "img", "aria-label": title } : { "aria-hidden": true };

  return (
    <svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg" fill="none" className={className} width={width} height={height} {...accessibility}>
      <ellipse cx="400" cy="508" rx="236" ry="20" style={fill(contrastColor)} opacity="0.08" />

      <g transform="rotate(-9 262 250)">
        <rect x="182" y="150" width="160" height="200" rx="16" style={fill(tintColor)} />
        <rect x="206" y="182" width="88" height="12" rx="6" style={fill(surfaceColor)} />
        <rect x="206" y="210" width="112" height="12" rx="6" style={fill(surfaceColor)} />
        <rect x="206" y="238" width="72" height="12" rx="6" style={fill(surfaceColor)} />
      </g>

      <g transform="rotate(8 548 232)">
        <rect x="468" y="132" width="160" height="200" rx="16" style={fill(tintColor)} />
        <rect x="492" y="164" width="96" height="12" rx="6" style={fill(surfaceColor)} />
        <rect x="492" y="192" width="112" height="12" rx="6" style={fill(surfaceColor)} />
        <rect x="492" y="220" width="64" height="12" rx="6" style={fill(surfaceColor)} />
      </g>

      <path
        style={fill(secondaryColor)}
        d="M220 262a24 24 0 0 1 24-24h96a24 24 0 0 1 18.2 8.4l19 22.2a8 8 0 0 0 6.1 2.8H556a24 24 0 0 1 24 24v184a24 24 0 0 1-24 24H244a24 24 0 0 1-24-24z"
      />
      <rect x="262" y="256" width="276" height="120" rx="12" style={fill(surfaceColor)} />
      <rect x="290" y="276" width="120" height="10" rx="5" style={fill(tintColor)} />
      <rect x="290" y="296" width="180" height="10" rx="5" style={fill(tintColor)} />
      <path style={fill(primaryColor)} d="M204 344a24 24 0 0 1 24-24h344a24 24 0 0 1 24 24l-14 142a24 24 0 0 1-24 22H242a24 24 0 0 1-24-22z" />

      <circle cx="566" cy="330" r="52" style={fill(surfaceColor)} />
      <circle cx="566" cy="330" r="42" style={fill(contrastColor)} />
      <rect x="544" y="324" width="44" height="12" rx="6" style={fill(surfaceColor)} />
      <rect x="560" y="308" width="12" height="44" rx="6" style={fill(surfaceColor)} />

      <circle cx="640" cy="250" r="8" style={fill(primaryColor)} opacity="0.5" />
      <circle cx="172" cy="400" r="10" style={fill(tintColor)} />
      <rect x="652" y="388" width="16" height="16" rx="4" style={fill(tintColor)} transform="rotate(45 660 396)" />
    </svg>
  );
}
