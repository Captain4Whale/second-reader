import type { MarkType } from "./contract";

type MarkMeta = {
  label: string;
};

const markMeta: Record<MarkType, MarkMeta> = {
  resonance: { label: "Resonance" },
  blindspot: { label: "Blindspot" },
  bookmark: { label: "Bookmark" },
};

export function markLabel(type: MarkType | string): string {
  return markMeta[type as MarkType]?.label ?? type;
}

