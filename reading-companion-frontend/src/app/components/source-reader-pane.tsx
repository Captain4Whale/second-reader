import {
  AlertCircle,
  ExternalLink,
  Loader2,
  Minus,
  Plus,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { SectionCard } from "../lib/api-types";
import type { ReactionType } from "../lib/contract";
import { reactionMeta } from "../lib/reactions";
import type {
  ReaderCapability,
  ReaderJumpFeedback,
  ReaderJumpRequest,
  ReaderLocation,
  ReaderLocationUpdate,
  ReaderTheme,
} from "../lib/reader-types";
import { normalizeReaderCharacter, normalizeReaderText } from "../lib/reader-types";
import { Switch } from "./ui/switch";

type EpubContents = {
  document?: Document;
  cfiFromRange?: (range: Range) => string;
};

type EpubRendition = {
  annotations?: {
    highlight: (cfiRange: string, data?: object, cb?: (...args: unknown[]) => void, className?: string, styles?: object) => void;
    remove: (cfiRange: string, type: string) => void;
  };
  destroy: () => void;
  display: (target?: string | number) => Promise<void>;
  getContents: () => EpubContents[] | EpubContents;
  hooks?: {
    content?: {
      register: (fn: (contents: EpubContents) => void) => void;
    };
  };
  next: () => Promise<void>;
  off: (type: string, listener: (...args: unknown[]) => void) => void;
  on: (type: string, listener: (...args: unknown[]) => void) => void;
  prev: () => Promise<void>;
  resize?: (width?: number, height?: number) => void;
  themes?: {
    fontSize: (size: string) => void;
    register: (name: string, rules: Record<string, Record<string, string>>) => void;
    select: (name: string) => void;
  };
};

type EpubBook = {
  destroy: () => void;
  locations?: {
    generate: (chars: number) => Promise<unknown>;
    percentageFromCfi?: (cfi: string) => number;
  };
  ready: Promise<void>;
  renderTo: (container: Element, options?: Record<string, unknown>) => EpubRendition;
};

type EpubCFIComparator = {
  compare: (a: string, b: string) => number;
};

type EpubCreateBook = (
  input: string | ArrayBuffer,
  options?: {
    openAs?: string;
  },
) => EpubBook;

type DisplayedLocation = {
  start?: {
    cfi?: string;
    href?: string;
    percentage?: number;
  };
};

interface SectionLocatorEntry {
  endCfi: string | null;
  href: string | null;
  sectionRef: string;
  startCfi: string | null;
}

export interface SourceReaderPaneProps {
  chapterRef: string;
  chapterTitle: string;
  followNotes: boolean;
  jumpRequest: ReaderJumpRequest | null;
  onFollowNotesChange: (value: boolean) => void;
  onLocationChange?: (update: ReaderLocationUpdate) => void;
  sections: SectionCard[];
  sourceUrl: string | null;
}

const FONT_SIZE_STEP = 8;
const FONT_SIZE_MIN = 84;
const FONT_SIZE_MAX = 148;
const FONT_SIZE_STORAGE_KEY = "chapter-reader-font-size";
const JUMP_DISPLAY_TIMEOUT_CFI_MS = 300;
const JUMP_DISPLAY_TIMEOUT_HREF_MS = 1100;
const JUMP_SPINNER_GUARD_MS = 2200;
const JUMP_SPINNER_DELAY_MS = 180;
const CFI_DISPLAY_FAIL_LIMIT = 2;
const CFI_DEGRADE_MIN_ATTEMPTS = 6;
const CFI_DEGRADE_FAILURE_RATIO = 0.7;
const PAPER_CANVAS_HEX = "#FAF7F2";
const PAPER_SHEET_HEX = "#FFFCF5";
const PAPER_RAIL_BORDER_HEX = "rgba(183, 162, 124, 0.18)";
const NIGHT_CANVAS_HEX = "#16120f";
const NIGHT_SHEET_HEX = "#1d1712";
const NIGHT_RAIL_BORDER_HEX = "rgba(108, 88, 62, 0.42)";

const READER_CAPABILITY: ReaderCapability = {
  cfiJump: true,
  hrefJump: true,
  textHighlight: true,
};

const PAPER_THEME = {
  body: {
    "background-color": PAPER_SHEET_HEX,
    color: "#2c1810",
    "font-family": "'Lora', Georgia, serif",
    "line-height": "1.8",
    margin: "0 auto",
    "max-width": "min(84rem, calc(100vw - 2.5rem))",
    width: "100%",
    "box-sizing": "border-box",
    padding: "1.25rem 2rem 3.5rem",
  },
  p: {
    "margin-bottom": "1.05rem",
  },
};

const NIGHT_THEME = {
  body: {
    "background-color": NIGHT_SHEET_HEX,
    color: "#e8ddcb",
    "font-family": "'Lora', Georgia, serif",
    "line-height": "1.8",
    margin: "0 auto",
    "max-width": "min(84rem, calc(100vw - 2.5rem))",
    width: "100%",
    "box-sizing": "border-box",
    padding: "1.25rem 2rem 3.5rem",
  },
  p: {
    "margin-bottom": "1.05rem",
  },
};

type ReaderHighlightTone = {
  className: string;
  fill: string;
  opacity: string;
};

const READER_HIGHLIGHT_ALPHA_LIGHT = 0.78;
const READER_HIGHLIGHT_ALPHA_NIGHT = 0.42;
const READER_HIGHLIGHT_FALLBACK_HEX = "#F6E3A5";

function hexToRgba(value: string, alpha: number): string {
  const normalized = value.trim().replace(/^#/, "");
  const parsed = normalized.length === 3
    ? normalized.split("").map((character) => Number.parseInt(character.repeat(2), 16))
    : normalized.match(/.{1,2}/g)?.map((segment) => Number.parseInt(segment, 16));

  if (!parsed || parsed.length < 3 || parsed.some((channel) => Number.isNaN(channel))) {
    return `rgba(212, 168, 64, ${alpha})`;
  }

  const [red, green, blue] = parsed;
  return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
}

function highlightToneForReactionType(
  reactionType: ReactionType | null | undefined,
  theme: ReaderTheme,
): ReaderHighlightTone {
  const alpha = theme === "night" ? READER_HIGHLIGHT_ALPHA_NIGHT : READER_HIGHLIGHT_ALPHA_LIGHT;
  const hex = reactionType ? reactionMeta[reactionType]?.surfaceHex : null;

  return {
    className: "rc-reader-highlight",
    fill: hexToRgba(hex ?? READER_HIGHLIGHT_FALLBACK_HEX, alpha),
    opacity: String(alpha),
  };
}

function readStoredFontSize(): number {
  if (typeof window === "undefined") {
    return 100;
  }
  const raw = window.localStorage.getItem(FONT_SIZE_STORAGE_KEY);
  if (!raw) {
    return 100;
  }
  const parsed = Number(raw);
  if (Number.isNaN(parsed)) {
    return 100;
  }
  return Math.min(FONT_SIZE_MAX, Math.max(FONT_SIZE_MIN, parsed));
}

function normalizeHref(value: string | null | undefined): string | null {
  if (!value) {
    return null;
  }
  const [withoutFragment] = value.split("#");
  const [path] = withoutFragment.split("?");
  const normalizedPath = path.replace(/^\.?\//, "").trim().toLowerCase();
  if (!normalizedPath) {
    return null;
  }
  try {
    return decodeURIComponent(normalizedPath);
  } catch {
    return normalizedPath;
  }
}

function hrefBaseName(value: string): string {
  const parts = value.split("/");
  return parts[parts.length - 1] ?? value;
}

function hrefEquivalent(left: string | null, right: string | null): boolean {
  if (!left || !right) {
    return false;
  }
  if (left === right) {
    return true;
  }
  if (left.endsWith(`/${right}`) || right.endsWith(`/${left}`)) {
    return true;
  }
  return hrefBaseName(left) === hrefBaseName(right);
}

function normalizeDisplayedLocation(raw: unknown): DisplayedLocation | null {
  if (!raw || typeof raw !== "object") {
    return null;
  }
  const candidate = raw as { start?: DisplayedLocation["start"] };
  return candidate.start ? { start: candidate.start } : null;
}

function compareCfi(comparator: EpubCFIComparator | null, first: string, second: string): number {
  if (!comparator) {
    return 0;
  }
  try {
    return comparator.compare(first, second);
  } catch {
    return 0;
  }
}

function cfiWithinRange(comparator: EpubCFIComparator | null, cfi: string, start: string | null, end: string | null): boolean {
  if (!start || !end) {
    return false;
  }

  const [lower, upper] = compareCfi(comparator, start, end) <= 0 ? [start, end] : [end, start];
  return compareCfi(comparator, cfi, lower) >= 0 && compareCfi(comparator, cfi, upper) <= 0;
}

function findSectionRefForLocation(
  entries: SectionLocatorEntry[],
  comparator: EpubCFIComparator | null,
  href: string | null,
  cfi: string | null,
): string | null {
  const normalizedHref = normalizeHref(href);
  const hrefMatches = normalizedHref
    ? entries.filter((entry) => hrefEquivalent(normalizeHref(entry.href), normalizedHref))
    : [];

  if (hrefMatches.length === 0) {
    return null;
  }
  if (!cfi) {
    return hrefMatches[0].sectionRef;
  }

  const precise = hrefMatches.find((entry) => cfiWithinRange(comparator, cfi, entry.startCfi, entry.endCfi));
  if (precise) {
    return precise.sectionRef;
  }

  if (!comparator) {
    return hrefMatches[0].sectionRef;
  }

  const withStart = hrefMatches.filter((entry) => entry.startCfi);
  if (withStart.length === 0) {
    return hrefMatches[0].sectionRef;
  }

  let closestBefore: SectionLocatorEntry | null = null;
  let closestAfter: SectionLocatorEntry | null = null;

  for (const entry of withStart) {
    const startCfi = entry.startCfi;
    if (!startCfi) {
      continue;
    }
    const delta = compareCfi(comparator, cfi, startCfi);
    if (delta >= 0) {
      if (
        !closestBefore ||
        compareCfi(comparator, startCfi, closestBefore.startCfi ?? startCfi) > 0
      ) {
        closestBefore = entry;
      }
      continue;
    }
    if (
      !closestAfter ||
      compareCfi(comparator, startCfi, closestAfter.startCfi ?? startCfi) < 0
    ) {
      closestAfter = entry;
    }
  }

  return closestBefore?.sectionRef ?? closestAfter?.sectionRef ?? hrefMatches[0].sectionRef;
}

function getContentsList(rendition: EpubRendition): EpubContents[] {
  const contents = rendition.getContents();
  if (!contents) {
    return [];
  }
  return Array.isArray(contents) ? contents : [contents];
}

function buildNormalizedIndexMap(value: string): { indices: number[]; normalized: string } {
  const indices: number[] = [];
  let normalized = "";
  let previousWhitespace = false;

  for (let index = 0; index < value.length; index += 1) {
    const normalizedCharacter = normalizeReaderCharacter(value[index]);
    if (normalizedCharacter === " ") {
      if (previousWhitespace) {
        continue;
      }
      previousWhitespace = true;
    } else {
      previousWhitespace = false;
    }

    normalized += normalizedCharacter;
    indices.push(index);
  }

  return { indices, normalized };
}

function findRangeByText(node: Text, query: string): Range | null {
  const value = node.nodeValue ?? "";
  if (!value || !query) {
    return null;
  }

  const start = value.indexOf(query);
  if (start === -1) {
    return null;
  }

  const range = node.ownerDocument.createRange();
  range.setStart(node, start);
  range.setEnd(node, start + query.length);
  return range;
}

function findRangeByNormalizedText(node: Text, normalizedQuery: string): Range | null {
  const value = node.nodeValue ?? "";
  if (!value || !normalizedQuery) {
    return null;
  }

  const mapped = buildNormalizedIndexMap(value);
  const startInNormalized = mapped.normalized.indexOf(normalizedQuery);
  if (startInNormalized === -1) {
    return null;
  }

  const start = mapped.indices[startInNormalized];
  const endNormalizedIndex = startInNormalized + normalizedQuery.length - 1;
  const end = mapped.indices[endNormalizedIndex] + 1;

  const range = node.ownerDocument.createRange();
  range.setStart(node, start);
  range.setEnd(node, end);
  return range;
}

function findTextRange(contents: EpubContents, text: string, normalized: boolean): Range | null {
  const document = contents.document;
  if (!document?.body) {
    return null;
  }

  const query = normalized ? normalizeReaderText(text) : text;
  if (!query) {
    return null;
  }

  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node = walker.nextNode();
  while (node) {
    const textNode = node as Text;
    const range = normalized
      ? findRangeByNormalizedText(textNode, query)
      : findRangeByText(textNode, text);
    if (range) {
      return range;
    }
    node = walker.nextNode();
  }
  return null;
}

function findRangeByParagraphIndex(contents: EpubContents, paragraphIndex: number): Range | null {
  const document = contents.document;
  if (!document?.body) {
    return null;
  }

  const blocks = Array.from(
    document.body.querySelectorAll("p, li, blockquote, h1, h2, h3, h4, h5, h6"),
  ).filter((element) => (element.textContent ?? "").trim().length > 0);

  if (blocks.length === 0) {
    return null;
  }

  const targetIndex = Math.max(0, Math.min(blocks.length - 1, paragraphIndex));
  const targetBlock = blocks[targetIndex];
  const range = document.createRange();
  range.selectNodeContents(targetBlock);
  return range;
}

function isRangeVisible(range: Range): boolean {
  const view = range.startContainer.ownerDocument.defaultView;
  if (!view) {
    return false;
  }

  const rect = range.getBoundingClientRect();
  if (!rect || (rect.height === 0 && rect.width === 0)) {
    return false;
  }

  const topSafeMargin = view.innerHeight * 0.08;
  const bottomSafeMargin = view.innerHeight * 0.08;
  return rect.top >= topSafeMargin && rect.bottom <= view.innerHeight - bottomSafeMargin;
}

function findReaderScrollContainer(frameElement: Element | null): HTMLElement | null {
  if (!frameElement) {
    return null;
  }
  if (frameElement instanceof HTMLElement) {
    const nearest = frameElement.closest(".epub-container");
    if (nearest instanceof HTMLElement) {
      return nearest;
    }
  }

  const ownerDocument = frameElement.ownerDocument;
  const candidates = Array.from(ownerDocument.querySelectorAll<HTMLElement>(".epub-container"));
  const containing = candidates.find((candidate) => candidate.contains(frameElement));
  if (containing) {
    return containing;
  }

  return frameElement.parentElement instanceof HTMLElement ? frameElement.parentElement : null;
}

function scrollRangeIntoView(range: Range): void {
  const container =
    (range.startContainer.nodeType === Node.ELEMENT_NODE
      ? (range.startContainer as Element)
      : range.startContainer.parentElement) ??
    null;

  if (!isRangeVisible(range) && container) {
    container.scrollIntoView({
      behavior: "auto",
      block: "center",
      inline: "nearest",
    });
  }

  const view = range.startContainer.ownerDocument.defaultView;
  const frameElement = view?.frameElement;
  if (!view || !(frameElement instanceof Element)) {
    return;
  }

  const outerContainer = findReaderScrollContainer(frameElement);
  if (!outerContainer) {
    return;
  }

  const innerRect = range.getBoundingClientRect();
  if (!innerRect || (innerRect.height === 0 && innerRect.width === 0)) {
    return;
  }

  const frameRect = frameElement.getBoundingClientRect();
  const outerRect = outerContainer.getBoundingClientRect();
  const targetTop = frameRect.top + innerRect.top;
  const targetBottom = frameRect.top + innerRect.bottom;
  const safeTop = outerRect.top + outerRect.height * 0.18;
  const safeBottom = outerRect.bottom - outerRect.height * 0.18;

  let delta = 0;
  if (targetTop < safeTop) {
    delta = targetTop - safeTop;
  } else if (targetBottom > safeBottom) {
    delta = targetBottom - safeBottom;
  }

  if (Math.abs(delta) < 2) {
    return;
  }

  outerContainer.scrollTo({
    top: Math.max(0, outerContainer.scrollTop + delta),
    behavior: "auto",
  });
}

function formatProgress(value: number | null): string {
  if (value == null || Number.isNaN(value)) {
    return "--";
  }
  return `${Math.round(value * 100)}%`;
}

function disableSmoothScrollInHost(host: HTMLElement): void {
  host.style.scrollBehavior = "auto";
  const descendants = host.querySelectorAll<HTMLElement>("*");
  descendants.forEach((element) => {
    element.style.scrollBehavior = "auto";
  });
}

function applyReaderThemeFlag(doc: Document, theme: ReaderTheme): void {
  doc.documentElement.setAttribute("data-rc-theme", theme);
}

function applyReaderThemeToVisibleContents(rendition: EpubRendition, theme: ReaderTheme): void {
  const contentsList = getContentsList(rendition);
  contentsList.forEach((contents) => {
    if (contents.document) {
      applyReaderThemeFlag(contents.document, theme);
    }
  });
}

function noop(): void {}

function normalizeJumpTarget(target: string | null | undefined): string | null {
  if (!target) {
    return null;
  }
  const normalized = target.trim();
  return normalized.length > 0 ? normalized : null;
}

function isRangeCfi(target: string): boolean {
  const normalized = target.trim();
  if (!normalized.startsWith("epubcfi(")) {
    return false;
  }
  return normalized.includes(",");
}

function isCfiTarget(target: string): boolean {
  return target.trim().startsWith("epubcfi(");
}

export function SourceReaderPane({
  sourceUrl,
  chapterRef,
  chapterTitle,
  sections,
  jumpRequest,
  followNotes,
  onFollowNotesChange,
  onLocationChange = noop,
}: SourceReaderPaneProps) {
  const sectionLocators = useMemo<SectionLocatorEntry[]>(
    () =>
      sections.map((section) => ({
        endCfi: section.locator?.end_cfi ?? null,
        href: section.locator?.href ?? null,
        sectionRef: section.section_ref,
        startCfi: section.locator?.start_cfi ?? null,
      })),
    [sections],
  );

  const [fontSize, setFontSize] = useState(readStoredFontSize);
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [readerReady, setReaderReady] = useState(false);
  const [lastJumpFeedback, setLastJumpFeedback] = useState<ReaderJumpFeedback | null>(null);
  const [isJumping, setIsJumping] = useState(false);
  const [readerLocation, setReaderLocation] = useState<ReaderLocation>({
    cfi: null,
    href: null,
    progress: null,
    sectionRef: null,
  });

  const hostRef = useRef<HTMLDivElement | null>(null);
  const bookRef = useRef<EpubBook | null>(null);
  const renditionRef = useRef<EpubRendition | null>(null);
  const comparatorRef = useRef<EpubCFIComparator | null>(null);
  const currentHighlightRef = useRef<string | null>(null);
  const highlightCfisRef = useRef<Set<string>>(new Set());
  const lastHandledJumpIdRef = useRef<number | null>(null);
  const activeProgrammaticJumpRef = useRef<number | null>(null);
  const activeProgrammaticSectionRefRef = useRef<string | null>(null);
  const activeJumpRunRef = useRef(0);
  const failedDisplayTargetsRef = useRef<Map<string, number>>(new Map());
  const cfiDisplayStatsRef = useRef({
    attempts: 0,
    degraded: false,
    failures: 0,
  });
  const resizeRafRef = useRef<number | null>(null);
  const sectionLocatorsRef = useRef<SectionLocatorEntry[]>(sectionLocators);
  const onLocationChangeRef = useRef(onLocationChange);
  const theme: ReaderTheme = "paper";
  const themeRef = useRef<ReaderTheme>("paper");

  useEffect(() => {
    sectionLocatorsRef.current = sectionLocators;
  }, [sectionLocators]);

  useEffect(() => {
    onLocationChangeRef.current = onLocationChange;
  }, [onLocationChange]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(FONT_SIZE_STORAGE_KEY, String(fontSize));
    }
  }, [fontSize]);

  useEffect(() => {
    const host = hostRef.current;
    const rendition = renditionRef.current;
    if (!host || !rendition?.resize || typeof ResizeObserver === "undefined") {
      return;
    }

    const applyResize = () => {
      const rect = host.getBoundingClientRect();
      if (rect.width <= 0 || rect.height <= 0) {
        return;
      }
      rendition.resize?.(Math.floor(rect.width), Math.floor(rect.height));
    };

    applyResize();
    const observer = new ResizeObserver(() => {
      if (resizeRafRef.current != null) {
        window.cancelAnimationFrame(resizeRafRef.current);
      }
      resizeRafRef.current = window.requestAnimationFrame(() => {
        resizeRafRef.current = null;
        applyResize();
      });
    });
    observer.observe(host);

    return () => {
      observer.disconnect();
      if (resizeRafRef.current != null) {
        window.cancelAnimationFrame(resizeRafRef.current);
        resizeRafRef.current = null;
      }
    };
  }, [readerReady, sourceUrl]);

  useEffect(() => {
    const rendition = renditionRef.current;
    if (!rendition?.themes) {
      return;
    }
    rendition.themes.fontSize(`${fontSize}%`);
  }, [fontSize]);

  useEffect(() => {
    const rendition = renditionRef.current;
    if (!rendition?.themes) {
      return;
    }
    rendition.themes.select(theme);
    applyReaderThemeToVisibleContents(rendition, theme);
  }, [theme]);

  useEffect(() => {
    let cancelled = false;

    async function setupReader() {
      if (!sourceUrl || !hostRef.current) {
        return;
      }

      setIsLoading(true);
      setReaderReady(false);
      setLoadError(null);
      setLastJumpFeedback(null);
      lastHandledJumpIdRef.current = null;
      activeProgrammaticJumpRef.current = null;

      try {
        const module = await import("epubjs");
        const createBook = module.default as unknown as EpubCreateBook;
        const comparator = "EpubCFI" in module
          ? new (module.EpubCFI as unknown as { new (): EpubCFIComparator })()
          : null;

        if (cancelled) {
          return;
        }

        // Backend source endpoint does not end with ".epub", so force zip parsing mode.
        const book = createBook(sourceUrl, { openAs: "epub" });
        const rendition = book.renderTo(hostRef.current, {
          flow: "scrolled-doc",
          manager: "continuous",
          spread: "none",
          width: "100%",
          height: "100%",
        });
        disableSmoothScrollInHost(hostRef.current);

        bookRef.current = book;
        renditionRef.current = rendition;
        comparatorRef.current = comparator;

        rendition.hooks?.content?.register((contents) => {
          if (contents.document) {
            applyReaderThemeFlag(contents.document, themeRef.current);
          }
          // Inject one highlight class for annotation-driven target emphasis.
          void contents.document?.head?.insertAdjacentHTML(
            "beforeend",
            `<style id="rc-reader-highlight-style">
              html {
                box-sizing: border-box !important;
                background: ${PAPER_CANVAS_HEX} !important;
              }
              html[data-rc-theme="night"] {
                background: ${NIGHT_CANVAS_HEX} !important;
              }
              html, body {
                width: 100% !important;
                box-sizing: border-box !important;
              }
              body {
                background: ${PAPER_SHEET_HEX} !important;
                max-width: min(84rem, calc(100vw - 2.5rem)) !important;
                margin: 0 auto !important;
                padding: 1.25rem 2rem 3.5rem !important;
                min-height: 100vh !important;
                border-left: 1px solid ${PAPER_RAIL_BORDER_HEX} !important;
                border-right: 1px solid ${PAPER_RAIL_BORDER_HEX} !important;
              }
              html[data-rc-theme="night"] body {
                background: ${NIGHT_SHEET_HEX} !important;
                border-left-color: ${NIGHT_RAIL_BORDER_HEX} !important;
                border-right-color: ${NIGHT_RAIL_BORDER_HEX} !important;
              }
              html, body, * {
                scroll-behavior: auto !important;
              }
              img, svg, video {
                max-width: 100% !important;
                height: auto !important;
              }
              .rc-reader-highlight {
                mix-blend-mode: multiply;
              }
              html[data-rc-theme="night"] .rc-reader-highlight {
                mix-blend-mode: screen;
              }
            </style>`,
          );
        });

        rendition.themes?.register("paper", PAPER_THEME);
        rendition.themes?.register("night", NIGHT_THEME);
        rendition.themes?.select(theme);
        rendition.themes?.fontSize(`${fontSize}%`);

        const onRelocated = (raw: unknown) => {
          const location = normalizeDisplayedLocation(raw);
          if (!location?.start) {
            return;
          }

          const progressFromEvent = typeof location.start.percentage === "number"
            ? location.start.percentage
            : null;
          const cfi = location.start.cfi ?? null;
          const fallbackProgress =
            cfi && book.locations?.percentageFromCfi
              ? book.locations.percentageFromCfi(cfi)
              : null;
          const href = location.start.href ?? null;
          const sectionRef = findSectionRefForLocation(
            sectionLocatorsRef.current,
            comparatorRef.current,
            href,
            cfi,
          );
          const effectiveSectionRef =
            activeProgrammaticJumpRef.current != null
              ? activeProgrammaticSectionRefRef.current ?? sectionRef
              : sectionRef;
          const update: ReaderLocation = {
            cfi,
            href,
            progress: progressFromEvent ?? fallbackProgress ?? null,
            sectionRef: effectiveSectionRef,
          };
          setReaderLocation(update);
          onLocationChangeRef.current({
            location: update,
            programmatic: activeProgrammaticJumpRef.current != null,
          });
        };

        rendition.on("relocated", onRelocated);

        await book.ready;
        if (cancelled) {
          return;
        }
        if (book.locations?.generate) {
          await book.locations.generate(1600);
        }

        const initialDisplayTarget =
          sectionLocatorsRef.current.find((entry) => entry.href)?.href ??
          sectionLocatorsRef.current.find((entry) => entry.startCfi)?.startCfi ??
          undefined;

        try {
          await rendition.display(initialDisplayTarget);
        } catch {
          await rendition.display();
        }
        if (cancelled) {
          return;
        }

        setReaderReady(true);
        setLastJumpFeedback({
          approximate: false,
          message: "Reader ready.",
          resolution: "book-start",
          sectionRef: null,
        });
      } catch (error) {
        if (cancelled) {
          return;
        }
        const message = error instanceof Error ? error.message : "Failed to initialize EPUB reader.";
        setLoadError(message);
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void setupReader();

    return () => {
      cancelled = true;
      currentHighlightRef.current = null;
      highlightCfisRef.current.clear();
      comparatorRef.current = null;
      lastHandledJumpIdRef.current = null;
      activeProgrammaticJumpRef.current = null;
      activeProgrammaticSectionRefRef.current = null;
      const rendition = renditionRef.current;
      const book = bookRef.current;
      renditionRef.current = null;
      bookRef.current = null;
      cfiDisplayStatsRef.current = {
        attempts: 0,
        degraded: false,
        failures: 0,
      };

      if (rendition) {
        try {
          rendition.destroy();
        } catch {
          // ignore teardown errors
        }
      }
      if (book) {
        try {
          book.destroy();
        } catch {
          // ignore teardown errors
        }
      }
    };
  }, [sourceUrl]);

  function clearHighlight() {
    const rendition = renditionRef.current;
    const trackedHighlightCfis = Array.from(highlightCfisRef.current);
    if (!rendition || trackedHighlightCfis.length === 0 || !rendition.annotations) {
      highlightCfisRef.current.clear();
      currentHighlightRef.current = null;
      document.querySelectorAll("g.rc-reader-highlight").forEach((node) => node.remove());
      return;
    }
    try {
      trackedHighlightCfis.forEach((cfiRange) => {
        try {
          rendition.annotations?.remove(cfiRange, "highlight");
        } catch {
          // ignore stale annotation removal errors
        }
      });
    } catch {
      // ignore unexpected annotation cleanup errors
    } finally {
      highlightCfisRef.current.clear();
      currentHighlightRef.current = null;
      document.querySelectorAll("g.rc-reader-highlight").forEach((node) => node.remove());
    }
  }

  function highlightCfi(cfiRange: string, reactionType: ReactionType | null | undefined): boolean {
    const rendition = renditionRef.current;
    if (!rendition?.annotations) {
      return false;
    }
    if (!isRangeCfi(cfiRange)) {
      return false;
    }
    const tone = highlightToneForReactionType(reactionType, themeRef.current);
    clearHighlight();
    try {
      rendition.annotations.highlight(cfiRange, { source: "reaction", reactionType: reactionType ?? null }, undefined, tone.className, {
        fill: tone.fill,
        "fill-opacity": tone.opacity,
      });
      currentHighlightRef.current = cfiRange;
      highlightCfisRef.current.add(cfiRange);
      return true;
    } catch {
      return false;
    }
  }

  async function locateMatchText(
    targetText: string,
    reactionType: ReactionType | null | undefined,
  ): Promise<"exact" | "normalized" | null> {
    const rendition = renditionRef.current;
    if (!rendition) {
      return null;
    }
    const contentsList = getContentsList(rendition);
    if (contentsList.length === 0) {
      return null;
    }

    for (const mode of ["exact", "normalized"] as const) {
      for (const contents of contentsList) {
        const range = findTextRange(contents, targetText, mode === "normalized");
        if (!range || !contents.cfiFromRange) {
          continue;
        }
        const cfiRange = contents.cfiFromRange(range);
        if (!cfiRange) {
          continue;
        }
        scrollRangeIntoView(range);
        const highlighted = highlightCfi(cfiRange, reactionType);
        if (highlighted) {
          return mode;
        }
      }
    }

    return null;
  }

  async function locateSectionParagraph(
    locator: NonNullable<ReaderJumpRequest["sectionLocator"]>,
    reactionType: ReactionType | null | undefined,
  ): Promise<boolean> {
    const rendition = renditionRef.current;
    if (!rendition) {
      return false;
    }

    if (locator.href) {
      try {
        await rendition.display(locator.href);
      } catch {
        // Keep trying in currently loaded contents.
      }
    }

    const contentsList = getContentsList(rendition);
    if (contentsList.length === 0) {
      return false;
    }

    const paragraphIndex = Math.max(0, (locator.paragraph_start ?? 1) - 1);
    for (const contents of contentsList) {
      const range = findRangeByParagraphIndex(contents, paragraphIndex);
      if (!range) {
        continue;
      }
      scrollRangeIntoView(range);
      if (!contents.cfiFromRange) {
        return true;
      }
      const cfiRange = contents.cfiFromRange(range);
      if (!cfiRange) {
        return true;
      }
      highlightCfi(cfiRange, reactionType);
      return true;
    }

    return false;
  }

  async function displayWithTimeout(rendition: EpubRendition, target: string): Promise<boolean> {
    const timeoutMs = isCfiTarget(target) ? JUMP_DISPLAY_TIMEOUT_CFI_MS : JUMP_DISPLAY_TIMEOUT_HREF_MS;
    try {
      await Promise.race([
        rendition.display(target),
        new Promise<never>((_, reject) => {
          window.setTimeout(() => reject(new Error("reader-display-timeout")), timeoutMs);
        }),
      ]);
      return true;
    } catch {
      return false;
    }
  }

  async function jumpToRequest(request: ReaderJumpRequest): Promise<void> {
    const rendition = renditionRef.current;
    if (!rendition) {
      return;
    }
    const runId = activeJumpRunRef.current + 1;
    activeJumpRunRef.current = runId;
    const isStale = () => activeJumpRunRef.current !== runId;
    const spinnerDelay = window.setTimeout(() => {
      if (!isStale()) {
        setIsJumping(true);
      }
    }, JUMP_SPINNER_DELAY_MS);
    const spinnerGuard = window.setTimeout(() => {
      if (activeJumpRunRef.current !== runId) {
        return;
      }
      activeProgrammaticJumpRef.current = null;
      activeProgrammaticSectionRefRef.current = null;
      setIsJumping(false);
      setLastJumpFeedback((current) => current ?? {
        approximate: true,
        message: "Positioning timed out. Stayed near current location.",
        resolution: "nearby",
        sectionRef: request.sectionRef,
      });
    }, JUMP_SPINNER_GUARD_MS);

    const displayTargets = [
      request.targetLocator?.start_cfi,
      request.targetLocator?.href,
      request.sectionLocator?.start_cfi,
      request.sectionLocator?.href,
      sectionLocators.find((entry) => entry.startCfi)?.startCfi,
      sectionLocators.find((entry) => entry.href)?.href,
    ].map(normalizeJumpTarget).filter((value): value is string => value != null);
    const uniqueTargets = [...new Set(displayTargets)];

    if (uniqueTargets.length === 0) {
      setLastJumpFeedback({
        approximate: true,
        message: "Reader opened, but this note has no locator.",
        resolution: "book-start",
        sectionRef: request.sectionRef,
      });
      if (!isStale()) {
        setIsJumping(false);
      }
      window.clearTimeout(spinnerDelay);
      window.clearTimeout(spinnerGuard);
      return;
    }

    activeProgrammaticJumpRef.current = request.id;
    activeProgrammaticSectionRefRef.current = request.sectionRef;
    clearHighlight();

    try {
      let displayed = false;
      for (const target of uniqueTargets) {
        if (isStale()) {
          return;
        }
        const isCfi = isCfiTarget(target);
        if (isCfi && cfiDisplayStatsRef.current.degraded) {
          continue;
        }
        const failureCount = failedDisplayTargetsRef.current.get(target) ?? 0;
        if (isCfi && failureCount >= CFI_DISPLAY_FAIL_LIMIT) {
          continue;
        }
        if (isCfi) {
          cfiDisplayStatsRef.current.attempts += 1;
        }
        // Try each locator in priority order; skip hung/invalid targets quickly.
        const success = await displayWithTimeout(rendition, target);
        if (success) {
          failedDisplayTargetsRef.current.delete(target);
          displayed = true;
          break;
        }
        if (isCfi) {
          failedDisplayTargetsRef.current.set(target, failureCount + 1);
          cfiDisplayStatsRef.current.failures += 1;
          const { attempts, failures } = cfiDisplayStatsRef.current;
          if (
            attempts >= CFI_DEGRADE_MIN_ATTEMPTS &&
            failures / attempts >= CFI_DEGRADE_FAILURE_RATIO
          ) {
            cfiDisplayStatsRef.current.degraded = true;
          }
        }
      }
      if (!displayed) {
        setLastJumpFeedback({
          approximate: true,
          message: "Locator timed out, stayed near current location.",
          resolution: "chapter-start",
          sectionRef: request.sectionRef,
        });
        return;
      }
      if (isStale()) {
        return;
      }

      if (request.targetLocator?.match_text) {
        const mode = await locateMatchText(request.targetLocator.match_text, request.reactionType);
        if (isStale()) {
          return;
        }
        if (mode === "exact") {
          setLastJumpFeedback({
            approximate: false,
            message: "Matched and highlighted exact quote.",
            resolution: "exact",
            sectionRef: request.sectionRef,
          });
          return;
        }
        if (mode === "normalized") {
          setLastJumpFeedback({
            approximate: true,
            message: "Matched normalized quote near the anchor.",
            resolution: "normalized",
            sectionRef: request.sectionRef,
          });
          return;
        }
      }

      if (request.targetLocator?.start_cfi) {
        await displayWithTimeout(rendition, request.targetLocator.start_cfi);
        if (isStale()) {
          return;
        }
        if (highlightCfi(request.targetLocator.start_cfi, request.reactionType)) {
          setLastJumpFeedback({
            approximate: true,
            message: "Jumped to locator anchor.",
            resolution: "nearby",
            sectionRef: request.sectionRef,
          });
          return;
        }
      }

      if (request.sectionLocator) {
        const locatedByParagraph = await locateSectionParagraph(request.sectionLocator, request.reactionType);
        if (isStale()) {
          return;
        }
        if (locatedByParagraph) {
          setLastJumpFeedback({
            approximate: true,
            message: "Located nearby section context.",
            resolution: "nearby",
            sectionRef: request.sectionRef,
          });
          return;
        }
      }

      if (request.sectionLocator?.start_cfi) {
        await displayWithTimeout(rendition, request.sectionLocator.start_cfi);
        if (isStale()) {
          return;
        }
      }

      if (request.sectionLocator?.start_cfi && highlightCfi(request.sectionLocator.start_cfi, request.reactionType)) {
        setLastJumpFeedback({
          approximate: true,
          message: "Located nearby section context.",
          resolution: "nearby",
          sectionRef: request.sectionRef,
        });
        return;
      }

      setLastJumpFeedback({
        approximate: true,
        message: "Jumped to chapter start fallback.",
        resolution: "chapter-start",
        sectionRef: request.sectionRef,
      });
    } catch {
      setLastJumpFeedback({
        approximate: true,
        message: "Jump failed, reader stayed on current location.",
        resolution: "book-start",
        sectionRef: request.sectionRef,
      });
    } finally {
      window.setTimeout(() => {
        if (activeProgrammaticJumpRef.current === request.id && !isStale()) {
          activeProgrammaticJumpRef.current = null;
          activeProgrammaticSectionRefRef.current = null;
        }
      }, 140);
      if (!isStale()) {
        window.setTimeout(() => {
          if (!isStale()) {
            setIsJumping(false);
          }
        }, 120);
      }
      window.clearTimeout(spinnerDelay);
      window.clearTimeout(spinnerGuard);
    }
  }

  useEffect(() => {
    if (!jumpRequest || !readerReady) {
      return;
    }
    if (lastHandledJumpIdRef.current === jumpRequest.id) {
      return;
    }
    lastHandledJumpIdRef.current = jumpRequest.id;
    void jumpToRequest(jumpRequest);
  }, [jumpRequest, readerReady]);

  const effectiveSectionRef =
    readerLocation.sectionRef ??
    lastJumpFeedback?.sectionRef ??
    jumpRequest?.sectionRef ??
    null;
  const currentSection = useMemo(
    () => sections.find((section) => section.section_ref === effectiveSectionRef) ?? null,
    [effectiveSectionRef, sections],
  );
  const currentSectionLabel = currentSection?.summary?.trim() || chapterTitle || chapterRef;
  const currentSectionMeta = effectiveSectionRef || chapterRef;
  const selectionStateLabel = followNotes ? "Following selected note" : "Free reading";
  const iconButtonClass = "inline-flex h-8 w-8 items-center justify-center rounded-full border border-[var(--warm-300)]/65 text-[var(--warm-700)] transition-colors";
  const followStateToneClass = followNotes ? "text-emerald-700" : "text-amber-700";
  const readerShellClass = "bg-[var(--warm-100)]";
  const loadingOverlayClass = "bg-[var(--warm-50)]/86";
  const loadingTextClass = "text-[var(--warm-700)]";
  const errorOverlayClass = "bg-[var(--warm-100)]";

  return (
    <div className={`h-full flex flex-col ${readerShellClass}`} data-testid="source-reader-pane">
      <div className="px-4 py-3 border-b border-[var(--warm-200)] bg-[var(--warm-50)]">
        <div className="flex items-end justify-between gap-3">
          <div className="min-w-0">
            <p className="text-[var(--warm-500)] uppercase tracking-[0.16em]" style={{ fontSize: "0.63rem", fontWeight: 600 }}>
              Reading in
            </p>
            <p
              className="text-[var(--warm-900)] truncate mt-0.5"
              style={{ fontSize: "1.2rem", fontWeight: 700, lineHeight: 1.25 }}
              data-testid="reader-current-target"
            >
              {currentSectionLabel}
            </p>
            <div className="mt-2 flex items-center gap-2 min-w-0">
              <span
                className="inline-flex h-7 items-center rounded-full border border-[var(--warm-300)]/65 bg-white px-3 text-[var(--warm-700)]"
                style={{ fontSize: "0.74rem", fontWeight: 600 }}
              >
                {currentSectionMeta}
              </span>
              <p className="truncate text-[var(--warm-500)]" style={{ fontSize: "0.78rem", lineHeight: 1.5 }}>
                {selectionStateLabel}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-[var(--warm-500)]" style={{ fontSize: "0.7rem" }}>
              Progress
            </p>
            <p className="text-[var(--warm-800)]" style={{ fontSize: "1.35rem", lineHeight: 1.1, fontWeight: 700 }} data-testid="reader-progress">
              {formatProgress(readerLocation.progress)}
            </p>
          </div>
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setFontSize((current) => Math.max(FONT_SIZE_MIN, current - FONT_SIZE_STEP))}
            className={iconButtonClass}
            aria-label="Decrease font size"
          >
            <Minus className="w-3.5 h-3.5" />
          </button>
          <span className="text-[var(--warm-600)]" style={{ fontSize: "0.72rem", minWidth: "2.2rem", textAlign: "center" }}>
            {fontSize}%
          </span>
          <button
            type="button"
            onClick={() => setFontSize((current) => Math.min(FONT_SIZE_MAX, current + FONT_SIZE_STEP))}
            className={iconButtonClass}
            aria-label="Increase font size"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>

          <span className="mx-1 h-4 w-px bg-[var(--warm-300)]/60" />

          <div className="inline-flex h-8 items-center gap-2 rounded-full border border-[var(--warm-300)]/65 bg-white px-3">
            <Switch
              checked={followNotes}
              onCheckedChange={onFollowNotesChange}
              data-testid="reader-follow-notes"
              aria-label="Follow notes"
            />
            <span className={followStateToneClass} style={{ fontSize: "0.72rem", fontWeight: 600 }}>
              Follow notes {followNotes ? "on" : "off"}
            </span>
          </div>
        </div>

        {!followNotes ? (
          <p className="mt-1 text-[var(--amber-accent)]" style={{ fontSize: "0.72rem", fontWeight: 500 }} data-testid="reader-follow-hint">
            你正在自由阅读
          </p>
        ) : null}

        <div className="mt-2 flex items-center gap-3">
          <p
            className={`flex items-center gap-1 ${
              isJumping
                ? "text-[var(--warm-700)]"
                : lastJumpFeedback?.approximate
                  ? "text-[var(--warm-700)]"
                  : "text-[var(--amber-accent)]"
            }`}
            style={{ fontSize: "0.72rem" }}
            data-testid="reader-jump-status"
          >
            {isJumping ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : lastJumpFeedback?.approximate ? (
              <AlertCircle className="w-3.5 h-3.5" />
            ) : (
              <ExternalLink className="w-3.5 h-3.5" />
            )}
            {isJumping ? "Positioning in source..." : lastJumpFeedback?.message ?? "Waiting for note selection."}
          </p>
        </div>
      </div>

      <div className={`flex-1 relative overflow-hidden ${readerShellClass}`}>
        <div ref={hostRef} className={`absolute inset-0 ${readerShellClass}`} data-testid="source-reader-canvas" />

        {isLoading ? (
          <div className={`absolute inset-0 flex items-center justify-center ${loadingOverlayClass}`}>
            <p className={`inline-flex items-center gap-2 ${loadingTextClass}`} style={{ fontSize: "0.84rem" }}>
              <Loader2 className="w-4 h-4 animate-spin" />
              Loading source EPUB...
            </p>
          </div>
        ) : null}

        {loadError ? (
          <div className={`absolute inset-0 flex items-center justify-center p-6 ${errorOverlayClass}`}>
            <div className="max-w-md text-center">
              <p className="text-[var(--destructive)] mb-2" style={{ fontSize: "0.9rem", fontWeight: 600 }}>
                Reader unavailable
              </p>
              <p className="text-[var(--warm-700)]" style={{ fontSize: "0.84rem", lineHeight: 1.7 }}>
                {loadError}
              </p>
              <p className="mt-2 text-[var(--warm-500)]" style={{ fontSize: "0.78rem", lineHeight: 1.6 }}>
                Capability: CFI jump {READER_CAPABILITY.cfiJump ? "on" : "off"} · Href jump {READER_CAPABILITY.hrefJump ? "on" : "off"} ·
                Text highlight {READER_CAPABILITY.textHighlight ? "on" : "off"}
              </p>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
