import type { CSSProperties } from "react";

function scaledReaderToken(variableName: string): string {
  return `calc(var(${variableName}) * var(--rc-reading-font-scale, 1))`;
}

export const uiTypography = {
  shellBrand: {
    fontFamily: "var(--rc-font-serif)",
    fontSize: "var(--rc-type-shell-brand)",
    fontWeight: 600,
    lineHeight: 1.1,
  },
  shellTagline: {
    fontSize: "var(--rc-type-shell-tagline)",
    lineHeight: 1.1,
  },
  eyebrow: {
    fontSize: "var(--rc-type-eyebrow)",
    fontWeight: 600,
    lineHeight: 1.3,
  },
  pageTitle: {
    fontFamily: "var(--rc-font-serif)",
    fontSize: "var(--rc-type-page-title)",
    fontWeight: 600,
    lineHeight: 1.15,
  },
  cardTitle: {
    fontFamily: "var(--rc-font-serif)",
    fontSize: "var(--rc-type-card-title)",
    fontWeight: 600,
    lineHeight: 1.5,
  },
  panelTitle: {
    fontFamily: "var(--rc-font-serif)",
    fontSize: "var(--rc-type-panel-title)",
    fontWeight: 600,
    lineHeight: 1.35,
  },
  body: {
    fontSize: "var(--rc-type-body)",
    lineHeight: 1.7,
  },
  bodyMedium: {
    fontSize: "var(--rc-type-body)",
    fontWeight: 500,
    lineHeight: 1.35,
  },
  bodyStrong: {
    fontSize: "var(--rc-type-body)",
    fontWeight: 600,
    lineHeight: 1.35,
  },
  meta: {
    fontSize: "var(--rc-type-meta)",
    lineHeight: 1.5,
  },
  metaMedium: {
    fontSize: "var(--rc-type-meta)",
    fontWeight: 500,
    lineHeight: 1.35,
  },
  metaStrong: {
    fontSize: "var(--rc-type-meta)",
    fontWeight: 600,
    lineHeight: 1.35,
  },
  caption: {
    fontSize: "var(--rc-type-caption)",
    lineHeight: 1.55,
  },
  captionMedium: {
    fontSize: "var(--rc-type-caption)",
    fontWeight: 500,
    lineHeight: 1.45,
  },
  captionStrong: {
    fontSize: "var(--rc-type-caption)",
    fontWeight: 600,
    lineHeight: 1.3,
  },
  chip: {
    fontSize: "var(--rc-type-chip)",
    fontWeight: 600,
    lineHeight: 1.3,
  },
  control: {
    fontSize: "var(--rc-type-control)",
    fontWeight: 500,
    lineHeight: 1.35,
  },
  controlStrong: {
    fontSize: "var(--rc-type-control)",
    fontWeight: 600,
    lineHeight: 1.2,
  },
  controlCompact: {
    fontSize: "var(--rc-type-control-compact)",
    fontWeight: 600,
    lineHeight: 1.2,
  },
  actionSmall: {
    fontSize: "var(--rc-type-action-sm)",
    fontWeight: 500,
    lineHeight: 1.35,
  },
} satisfies Record<string, CSSProperties>;

export const readerTypography = {
  body: {
    fontSize: scaledReaderToken("--rc-type-reader-body"),
    lineHeight: 1.82,
  },
  bodyStrong: {
    fontSize: scaledReaderToken("--rc-type-reader-body"),
    fontWeight: 600,
    lineHeight: 1.7,
  },
  quote: {
    fontSize: scaledReaderToken("--rc-type-reader-quote"),
    lineHeight: 1.7,
  },
  meta: {
    fontSize: scaledReaderToken("--rc-type-reader-meta"),
    lineHeight: 1.6,
  },
  metaMedium: {
    fontSize: scaledReaderToken("--rc-type-reader-meta"),
    fontWeight: 500,
    lineHeight: 1.55,
  },
  metaStrong: {
    fontSize: scaledReaderToken("--rc-type-reader-meta"),
    fontWeight: 600,
    lineHeight: 1.45,
  },
  label: {
    fontSize: scaledReaderToken("--rc-type-reader-label"),
    fontWeight: 600,
    lineHeight: 1.35,
  },
  chip: {
    fontSize: scaledReaderToken("--rc-type-reader-chip"),
    fontWeight: 600,
    lineHeight: 1.3,
  },
  caption: {
    fontSize: scaledReaderToken("--rc-type-reader-caption"),
    lineHeight: 1.5,
  },
  captionStrong: {
    fontSize: scaledReaderToken("--rc-type-reader-caption"),
    fontWeight: 600,
    lineHeight: 1.3,
  },
} satisfies Record<string, CSSProperties>;

