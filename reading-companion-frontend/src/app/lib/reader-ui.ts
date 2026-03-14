"use client";

export const READER_FONT_SIZE_STEP = 8;
export const READER_FONT_SIZE_MIN = 84;
export const READER_FONT_SIZE_MAX = 148;
export const READER_FONT_SIZE_STORAGE_KEY = "chapter-reader-font-size";

export function clampReaderFontSize(value: number): number {
  return Math.min(READER_FONT_SIZE_MAX, Math.max(READER_FONT_SIZE_MIN, value));
}

export function readStoredReaderFontSize(): number {
  if (typeof window === "undefined") {
    return 100;
  }

  const raw = window.localStorage.getItem(READER_FONT_SIZE_STORAGE_KEY);
  if (!raw) {
    return 100;
  }

  const parsed = Number(raw);
  if (Number.isNaN(parsed)) {
    return 100;
  }

  return clampReaderFontSize(parsed);
}

export function formatReaderProgress(value: number | null): string {
  if (value == null || Number.isNaN(value)) {
    return "--";
  }
  return `${Math.round(value * 100)}%`;
}
