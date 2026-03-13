import { AlertTriangle, ArrowLeft, CheckCircle2, ChevronRight, CircleDashed, List, Loader2, Search } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router";
import {
  BookDetailResponse,
  ChapterDetailResponse,
  ChapterOutlineResponse,
  deleteReactionMark,
  fetchBookDetail,
  fetchChapterDetail,
  fetchChapterOutline,
  putReactionMark,
  toApiAssetUrl,
} from "../lib/api";
import type { ChapterListItem, ChapterOutlineSectionItem, SectionCard } from "../lib/api-types";
import {
  type MarkType,
  type ReactionFilter,
  REACTION_FILTERS,
  canonicalBookPath,
  canonicalChapterPath,
  type ReactionId,
} from "../lib/contract";
import { markLabel } from "../lib/marks";
import {
  buildSectionJumpRequest,
  buildReaderJumpRequest,
  findSelectionByReactionId,
  reactionPreview,
  type ReaderJumpRequest,
  type ReaderLocationUpdate,
  type ReaderPanelMode,
} from "../lib/reader-types";
import { reactionLabel, reactionMeta } from "../lib/reactions";
import { ErrorState, LoadingState } from "./page-state";
import { SourceReaderPane } from "./source-reader-pane";
import { OverflowTooltipText } from "./ui/overflow-tooltip-text";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "./ui/sheet";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "./ui/resizable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { useIsMobile } from "./ui/use-mobile";

const FOLLOW_NOTES_STORAGE_KEY = "chapter-reader-follow-notes";
const CHAPTER_FILTER_STORAGE_KEY_PREFIX = "chapter-reader-filter";
const CHAPTER_PANEL_MODE_STORAGE_KEY_PREFIX = "chapter-reader-panel-mode";
const CHAPTER_SECTION_HINT_STORAGE_KEY_PREFIX = "chapter-reader-section-hint";
const NOTE_CLICK_JUMP_THROTTLE_MS = 140;

function replaceReaction(
  payload: ChapterDetailResponse,
  reactionId: ReactionId,
  updater: (markType: MarkType | null) => MarkType | null,
): ChapterDetailResponse {
  return {
    ...payload,
    sections: payload.sections.map((section) => ({
      ...section,
      reactions: section.reactions.map((reaction) =>
        reaction.reaction_id === reactionId
          ? { ...reaction, mark_type: updater(reaction.mark_type ?? null) }
          : reaction,
      ),
    })),
  };
}

function parseReactionSearch(search: string): ReactionId | null {
  const params = new URLSearchParams(search);
  const value = params.get("reaction");
  if (!value) {
    return null;
  }
  const parsed = Number(value);
  if (!Number.isInteger(parsed)) {
    return null;
  }
  return parsed;
}

function parseSectionSearch(search: string): string | null {
  const params = new URLSearchParams(search);
  const value = params.get("section");
  const normalized = value?.trim();
  return normalized ? normalized : null;
}

function readFollowNotesPreference(): boolean {
  if (typeof window === "undefined") {
    return true;
  }
  return window.localStorage.getItem(FOLLOW_NOTES_STORAGE_KEY) !== "off";
}

function chapterFilterStorageKey(bookId: string): string {
  return `${CHAPTER_FILTER_STORAGE_KEY_PREFIX}:${bookId}`;
}

function chapterPanelModeStorageKey(bookId: string): string {
  return `${CHAPTER_PANEL_MODE_STORAGE_KEY_PREFIX}:${bookId}`;
}

function chapterSectionHintStorageKey(bookId: string, chapterId: number): string {
  return `${CHAPTER_SECTION_HINT_STORAGE_KEY_PREFIX}:${bookId}:${chapterId}`;
}

function readChapterFilterPreference(bookId: string): ReactionFilter {
  if (typeof window === "undefined" || !bookId) {
    return "all";
  }
  const persisted = window.sessionStorage.getItem(chapterFilterStorageKey(bookId));
  return persisted && REACTION_FILTERS.includes(persisted as ReactionFilter)
    ? (persisted as ReactionFilter)
    : "all";
}

function readChapterPanelModePreference(bookId: string): ReaderPanelMode {
  if (typeof window === "undefined" || !bookId) {
    return "notes";
  }
  const persisted = window.sessionStorage.getItem(chapterPanelModeStorageKey(bookId));
  return persisted === "book" ? "book" : "notes";
}

function filterSections(sections: SectionCard[], activeFilter: ReactionFilter): SectionCard[] {
  return sections
    .map((section) => ({
      ...section,
      reactions: activeFilter === "all"
        ? section.reactions
        : section.reactions.filter((reaction) => reaction.type === activeFilter),
    }))
    .filter((section) => section.reactions.length > 0);
}

function firstReactionId(sections: SectionCard[]): ReactionId | null {
  return sections.flatMap((section) => section.reactions)[0]?.reaction_id ?? null;
}

function initialReactionIdForFilter(
  sections: SectionCard[],
  activeFilter: ReactionFilter,
): ReactionId | null {
  return firstReactionId(filterSections(sections, activeFilter)) ?? firstReactionId(sections);
}

function findSectionByRef(sections: SectionCard[], sectionRef: string | null): SectionCard | null {
  if (!sectionRef) {
    return null;
  }
  return sections.find((section) => section.section_ref === sectionRef) ?? null;
}

function sectionHasVisibleReactions(section: SectionCard | null, activeFilter: ReactionFilter): boolean {
  if (!section) {
    return false;
  }
  if (activeFilter === "all") {
    return section.reactions.length > 0;
  }
  return section.reactions.some((reaction) => reaction.type === activeFilter);
}

function outlinePreviewTextFromSection(section: SectionCard): string {
  const quoted = section.reactions.find((reaction) => reaction.anchor_quote.trim())?.anchor_quote.trim();
  if (quoted) {
    return reactionPreview(quoted, 110);
  }
  const content = section.reactions.find((reaction) => reaction.content.trim())?.content.trim();
  if (content) {
    return reactionPreview(content, 110);
  }
  return "";
}

function buildOutlineFromChapterPayload(
  payload: ChapterDetailResponse,
  chapterEntry: ChapterListItem | null,
): ChapterOutlineResponse {
  return {
    book_id: payload.book_id,
    chapter_id: payload.chapter_id,
    chapter_ref: chapterEntry?.chapter_ref || payload.chapter_ref,
    title: chapterEntry?.title || payload.title,
    result_ready: true,
    status: "completed",
    section_count: payload.sections.length,
    sections: payload.sections.map((section) => ({
      section_ref: section.section_ref,
      summary: section.summary,
      preview_text: outlinePreviewTextFromSection(section),
      visible_reaction_count: section.reactions.length,
      locator: section.locator ?? null,
    })),
  };
}

export function ChapterReadPage() {
  const { id = "", bookId = "", chapterId: chapterIdParam = "" } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const isMobile = useIsMobile();

  const resolvedBookId = id || bookId;
  const bookIdNumber = Number(resolvedBookId);
  const chapterNumber = Number(chapterIdParam);
  const [payload, setPayload] = useState<ChapterDetailResponse | null>(null);
  const [bookDetail, setBookDetail] = useState<BookDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeReactionId, setActiveReactionId] = useState<ReactionId | null>(null);
  const [activeFilter, setActiveFilter] = useState<ReactionFilter>(() => readChapterFilterPreference(resolvedBookId));
  const [reloadTick, setReloadTick] = useState(0);
  const [mobileMode, setMobileMode] = useState<ReaderPanelMode>(() => readChapterPanelModePreference(resolvedBookId));
  const [followNotes, setFollowNotes] = useState(readFollowNotesPreference);
  const [passiveSectionRef, setPassiveSectionRef] = useState<string | null>(null);
  const [jumpRequest, setJumpRequest] = useState<ReaderJumpRequest | null>(null);
  const [isChapterSheetOpen, setIsChapterSheetOpen] = useState(false);
  const [sectionHint, setSectionHint] = useState<string | null>(null);
  const [outlineCache, setOutlineCache] = useState<Record<number, ChapterOutlineResponse>>({});
  const [outlineLoadingIds, setOutlineLoadingIds] = useState<number[]>([]);
  const [previewChapterId, setPreviewChapterId] = useState<number | null>(null);
  const [mobileChapterSheetView, setMobileChapterSheetView] = useState<"chapters" | "sections">("chapters");
  const [pendingSectionScrollRef, setPendingSectionScrollRef] = useState<string | null>(null);

  const jumpSequenceRef = useRef(0);
  const lastNoteJumpAtRef = useRef(0);
  const sectionRefs = useRef(new Map<string, HTMLElement | null>());
  const hoverPreviewTimerRef = useRef<number | null>(null);
  const outlineCacheRef = useRef<Record<number, ChapterOutlineResponse>>({});
  const outlineRequestRef = useRef<Record<number, Promise<ChapterOutlineResponse> | undefined>>({});
  const handledSectionQueryKeyRef = useRef<string | null>(null);
  const activeFilterRef = useRef<ReactionFilter>(activeFilter);
  const queryReactionId = useMemo(() => parseReactionSearch(location.search), [location.search]);
  const querySectionRef = useMemo(() => parseSectionSearch(location.search), [location.search]);

  const queueReaderJump = useCallback(
    (reactionId: ReactionId, source: ReaderJumpRequest["source"], sourcePayload: ChapterDetailResponse | null) => {
      if (!sourcePayload) {
        return;
      }
      const selection = findSelectionByReactionId(sourcePayload.sections, reactionId);
      if (!selection) {
        return;
      }
      jumpSequenceRef.current += 1;
      setJumpRequest(buildReaderJumpRequest(selection, source, jumpSequenceRef.current));
    },
    [],
  );

  const queueSectionJump = useCallback(
    (section: SectionCard, source: ReaderJumpRequest["source"]) => {
      jumpSequenceRef.current += 1;
      setJumpRequest(buildSectionJumpRequest(section, source, jumpSequenceRef.current));
    },
    [],
  );

  const syncWorkspaceQuery = useCallback(
    (
      options: {
        reactionId?: ReactionId | null;
        sectionRef?: string | null;
        replace?: boolean;
      },
    ) => {
      const params = new URLSearchParams(location.search);
      if (options.reactionId == null) {
        params.delete("reaction");
      } else {
        params.set("reaction", String(options.reactionId));
        params.delete("section");
      }
      if (options.sectionRef == null) {
        params.delete("section");
      } else if (options.reactionId == null) {
        params.set("section", options.sectionRef);
      }
      const search = params.toString();
      const target = `${location.pathname}${search ? `?${search}` : ""}`;
      const current = `${location.pathname}${location.search}`;
      if (target === current) {
        return;
      }
      navigate(target, { replace: options.replace ?? false });
    },
    [location.pathname, location.search, navigate],
  );

  const syncReactionQuery = useCallback(
    (reactionId: ReactionId | null, replace = false) => {
      syncWorkspaceQuery({ reactionId, replace });
    },
    [syncWorkspaceQuery],
  );

  const ensureChapterOutline = useCallback(
    async (chapterId: number) => {
      const cached = outlineCacheRef.current[chapterId];
      if (cached) {
        return cached;
      }
      const inFlight = outlineRequestRef.current[chapterId];
      if (inFlight) {
        return inFlight;
      }

      setOutlineLoadingIds((current) => (current.includes(chapterId) ? current : [...current, chapterId]));
      const request = fetchChapterOutline(bookIdNumber, chapterId)
        .then((outline) => {
          outlineCacheRef.current = { ...outlineCacheRef.current, [chapterId]: outline };
          setOutlineCache((current) => ({ ...current, [chapterId]: outline }));
          return outline;
        })
        .finally(() => {
          delete outlineRequestRef.current[chapterId];
          setOutlineLoadingIds((current) => current.filter((value) => value !== chapterId));
        });
      outlineRequestRef.current[chapterId] = request;
      return request;
    },
    [bookIdNumber],
  );

  const activateSection = useCallback(
    (
      sectionRef: string,
      sourcePayload: ChapterDetailResponse,
      source: "section-click" | "section-query",
      options: { syncQuery?: boolean; replaceQuery?: boolean } = {},
    ) => {
      const targetSection = findSectionByRef(sourcePayload.sections, sectionRef);
      if (!targetSection) {
        return false;
      }

      const shouldFallbackToAll =
        activeFilter !== "all" && !sectionHasVisibleReactions(targetSection, activeFilter);

      if (shouldFallbackToAll) {
        const nextHint = `This section has no ${reactionLabel(activeFilter)} notes, showing all notes instead.`;
        if (typeof window !== "undefined") {
          window.sessionStorage.setItem(
            chapterSectionHintStorageKey(String(sourcePayload.book_id), sourcePayload.chapter_id),
            nextHint,
          );
        }
        setActiveFilter("all");
        window.setTimeout(() => {
          setSectionHint(nextHint);
        }, 0);
      } else {
        setSectionHint(null);
      }

      setActiveReactionId(null);
      setPassiveSectionRef(sectionRef);
      setPendingSectionScrollRef(sectionRef);
      queueSectionJump(targetSection, source);

      if (options.syncQuery !== false) {
        syncWorkspaceQuery({
          sectionRef,
          replace: options.replaceQuery ?? false,
        });
      }

      return true;
    },
    [activeFilter, queueSectionJump, syncWorkspaceQuery],
  );

  const selectReaction = useCallback(
    (
      reactionId: ReactionId,
      source: "note-click" | "deep-link" | "initial" = "note-click",
      sourcePayload: ChapterDetailResponse | null,
      options?: { forceJump?: boolean },
    ) => {
      const isSameReaction = activeReactionId === reactionId;
      setActiveReactionId(reactionId);
      setSectionHint(null);
      setPassiveSectionRef(null);

      if (source === "note-click") {
        syncReactionQuery(reactionId);
        const now = Date.now();
        const isRapidRepeat = now - lastNoteJumpAtRef.current < NOTE_CLICK_JUMP_THROTTLE_MS;
        // Always honor switching to a different note.
        // Only suppress extremely fast duplicate taps on the same note.
        const shouldJump = Boolean(options?.forceJump) || !isSameReaction || !isRapidRepeat;
        if (shouldJump) {
          queueReaderJump(reactionId, "note-click", sourcePayload);
          lastNoteJumpAtRef.current = now;
        }
        if (isMobile) {
          setMobileMode("book");
        }
        return;
      }

      if (source === "deep-link") {
        queueReaderJump(reactionId, "deep-link", sourcePayload);
        return;
      }

      queueReaderJump(reactionId, "initial", sourcePayload);
    },
    [activeReactionId, isMobile, queueReaderJump, syncReactionQuery],
  );

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(FOLLOW_NOTES_STORAGE_KEY, followNotes ? "on" : "off");
    }
  }, [followNotes]);

  useEffect(() => {
    outlineCacheRef.current = outlineCache;
  }, [outlineCache]);

  useEffect(() => {
    activeFilterRef.current = activeFilter;
  }, [activeFilter]);

  useEffect(() => {
    setActiveFilter(readChapterFilterPreference(resolvedBookId));
    setMobileMode(readChapterPanelModePreference(resolvedBookId));
  }, [resolvedBookId]);

  useEffect(() => {
    if (typeof window === "undefined" || !resolvedBookId) {
      return;
    }
    window.sessionStorage.setItem(chapterFilterStorageKey(resolvedBookId), activeFilter);
  }, [activeFilter, resolvedBookId]);

  useEffect(() => {
    if (typeof window === "undefined" || !resolvedBookId) {
      return;
    }
    window.sessionStorage.setItem(chapterPanelModeStorageKey(resolvedBookId), mobileMode);
  }, [mobileMode, resolvedBookId]);

  useEffect(() => {
    if (typeof window === "undefined" || !payload) {
      return;
    }
    const key = chapterSectionHintStorageKey(String(payload.book_id), payload.chapter_id);
    const persisted = window.sessionStorage.getItem(key);
    if (!persisted) {
      return;
    }
    setSectionHint(persisted);
    window.sessionStorage.removeItem(key);
  }, [payload]);

  useEffect(() => {
    setIsChapterSheetOpen(false);
    setMobileChapterSheetView("chapters");
    setPreviewChapterId(null);
    setSectionHint(null);
    handledSectionQueryKeyRef.current = null;
    if (hoverPreviewTimerRef.current != null) {
      window.clearTimeout(hoverPreviewTimerRef.current);
      hoverPreviewTimerRef.current = null;
    }
  }, [chapterNumber]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    void Promise.all([
      fetchChapterDetail(bookIdNumber, chapterNumber, { limit: 100 }),
      fetchBookDetail(bookIdNumber).catch(() => null),
    ])
      .then(([nextPayload, nextBookDetail]) => {
        if (!active) {
          return;
        }

        setPayload(nextPayload);
        setBookDetail(nextBookDetail);
        const nextChapterEntry =
          nextBookDetail?.chapters.find((chapter) => chapter.chapter_id === nextPayload.chapter_id) ?? null;
        const seededOutline = buildOutlineFromChapterPayload(nextPayload, nextChapterEntry);
        outlineCacheRef.current = { ...outlineCacheRef.current, [nextPayload.chapter_id]: seededOutline };
        setOutlineCache((current) => ({ ...current, [nextPayload.chapter_id]: current[nextPayload.chapter_id] ?? seededOutline }));

        const hasReactionQuery =
          queryReactionId != null && findSelectionByReactionId(nextPayload.sections, queryReactionId) != null;
        const hasSectionQuery = querySectionRef != null && findSectionByRef(nextPayload.sections, querySectionRef) != null;
        const initialReactionId =
          hasReactionQuery
            ? queryReactionId
            : hasSectionQuery
              ? null
              : initialReactionIdForFilter(nextPayload.sections, activeFilterRef.current) ?? null;

        setActiveReactionId(initialReactionId);
        if (initialReactionId != null) {
          queueReaderJump(
            initialReactionId,
            hasReactionQuery ? "deep-link" : "initial",
            nextPayload,
          );
        }
      })
      .catch((reason) => {
        if (!active) {
          return;
        }
        setBookDetail(null);
        setError(reason instanceof Error ? reason.message : "Failed to load chapter data.");
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [bookIdNumber, chapterNumber, queueReaderJump, reloadTick]);

  useEffect(() => {
    if (!payload || queryReactionId == null) {
      return;
    }
    if (queryReactionId === activeReactionId) {
      return;
    }

    const selection = findSelectionByReactionId(payload.sections, queryReactionId);
    if (!selection) {
      return;
    }
    selectReaction(queryReactionId, "deep-link", payload);
  }, [activeReactionId, payload, queryReactionId, selectReaction]);

  useEffect(() => {
    if (!payload || queryReactionId != null || !querySectionRef) {
      return;
    }

    const queryKey = `${payload.chapter_id}:${querySectionRef}`;
    if (handledSectionQueryKeyRef.current === queryKey) {
      return;
    }

    const handled = activateSection(querySectionRef, payload, "section-query", {
      syncQuery: false,
    });
    if (handled) {
      handledSectionQueryKeyRef.current = queryKey;
    }
  }, [activateSection, payload, queryReactionId, querySectionRef]);

  useEffect(() => {
    if (!isChapterSheetOpen || !payload) {
      return;
    }
    setPreviewChapterId(payload.chapter_id);
    if (isMobile) {
      setMobileChapterSheetView("chapters");
      return;
    }
    void ensureChapterOutline(payload.chapter_id);
  }, [ensureChapterOutline, isChapterSheetOpen, isMobile, payload]);

  useEffect(() => {
    if (!pendingSectionScrollRef) {
      return;
    }
    const node = sectionRefs.current.get(pendingSectionScrollRef);
    if (!node) {
      return;
    }
    node.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest" });
    setPendingSectionScrollRef(null);
  }, [activeFilter, payload, pendingSectionScrollRef]);

  useEffect(() => () => {
    if (hoverPreviewTimerRef.current != null) {
      window.clearTimeout(hoverPreviewTimerRef.current);
    }
  }, []);

  if (loading && !payload) {
    return <LoadingState title="Loading chapter workspace..." />;
  }

  if (error || !payload) {
    return (
      <ErrorState
        title="Chapter workspace is unavailable"
        message={error ?? "We could not load this chapter right now."}
        onRetry={() => {
          setPayload(null);
          setLoading(true);
          setError(null);
          setReloadTick((value) => value + 1);
        }}
        linkLabel="Back to books"
        linkTo="/books"
      />
    );
  }

  const availableFilters = payload.available_filters.filter(
    (filter): filter is ReactionFilter => REACTION_FILTERS.includes(filter as ReactionFilter),
  );
  const renderedFilters = Array.from(
    new Set<ReactionFilter>([
      ...((availableFilters.length > 0 ? availableFilters : REACTION_FILTERS) as readonly ReactionFilter[]),
      activeFilter,
    ]),
  );
  const visibleSections = filterSections(payload.sections, activeFilter);
  const pillBaseClass = "inline-flex items-center rounded-full border px-3.5 backdrop-blur-sm shadow-[0_1px_0_rgba(255,255,255,0.9),0_10px_24px_rgba(61,46,31,0.045)] transition-all duration-200";
  const workspaceActionClass = "inline-flex h-8 items-center gap-2 rounded-full border border-[var(--warm-300)]/60 bg-white/82 px-3.5 text-[var(--warm-700)] shadow-[0_1px_0_rgba(255,255,255,0.88),0_8px_20px_rgba(61,46,31,0.04)] transition-all duration-200 hover:-translate-y-[1px] hover:bg-white";
  const workspacePrimaryActionClass = `${workspaceActionClass} hover:border-[var(--amber-accent)]/35 hover:text-[var(--warm-900)]`;
  const workspaceSecondaryActionClass = `${workspaceActionClass} hover:border-[var(--warm-400)] hover:text-[var(--warm-800)]`;
  const filterInactiveClass = `${pillBaseClass} h-10 border-[var(--warm-300)]/65 bg-white/82 text-[var(--warm-600)] hover:-translate-y-[1px] hover:border-[var(--warm-400)] hover:bg-white hover:text-[var(--warm-800)]`;
  const filterActiveClass = `${pillBaseClass} h-10 border-[var(--amber-accent)]/35 bg-[var(--amber-bg)] text-[var(--amber-accent)] shadow-[0_1px_0_rgba(255,255,255,0.82),0_12px_28px_rgba(139,105,20,0.12)]`;
  const markButtonBaseClass = `${pillBaseClass} h-9 border-[var(--warm-300)]/65 bg-white/86 text-[var(--warm-600)] hover:-translate-y-[1px] hover:border-[var(--warm-400)] hover:bg-white`;
  const chapterItems = bookDetail?.chapters ?? [];
  const readableChapterCount = chapterItems.filter((chapter) => chapter.result_ready).length;
  const showChapterSwitcher = Boolean(bookDetail) && readableChapterCount > 1;
  const currentChapterEntry = chapterItems.find((chapter) => chapter.chapter_id === payload.chapter_id) ?? null;
  const currentChapterRef = currentChapterEntry?.chapter_ref || payload.chapter_ref;
  const currentChapterTitle = (currentChapterEntry?.title || payload.title || "").trim();
  const showSeparateChapterTitle = Boolean(currentChapterTitle) && currentChapterTitle !== currentChapterRef;
  const workspaceHeading = showSeparateChapterTitle ? currentChapterTitle : currentChapterRef;
  const previewChapter = chapterItems.find((chapter) => chapter.chapter_id === previewChapterId) ?? currentChapterEntry;
  const previewOutline = previewChapterId != null ? outlineCache[previewChapterId] ?? null : null;
  const previewOutlineLoading = previewChapterId != null && outlineLoadingIds.includes(previewChapterId);
  const currentReadingSectionRef =
    passiveSectionRef ??
    findSelectionByReactionId(payload.sections, activeReactionId)?.section.section_ref ??
    querySectionRef ??
    null;
  const previewSectionItems = previewOutline?.sections ?? [];

  async function toggleMark(
    reactionId: ReactionId,
    currentMark: MarkType | null,
    nextMark: MarkType,
  ) {
    try {
      if (currentMark === nextMark) {
        await deleteReactionMark(reactionId);
        setPayload((current) => (current ? replaceReaction(current, reactionId, () => null) : current));
        return;
      }

      await putReactionMark(reactionId, payload.book_id, nextMark);
      setPayload((current) => (current ? replaceReaction(current, reactionId, () => nextMark) : current));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Failed to update mark.");
    }
  }

  function handleFilterChange(filter: ReactionFilter) {
    if (typeof window !== "undefined") {
      window.sessionStorage.removeItem(chapterSectionHintStorageKey(String(payload.book_id), payload.chapter_id));
    }
    setSectionHint(null);
    setActiveFilter(filter);
  }

  function openChapter(chapterId: number, options: { sectionRef?: string | null } = {}) {
    const search = options.sectionRef ? `?section=${encodeURIComponent(options.sectionRef)}` : "";
    if (chapterId === payload.chapter_id) {
      if (options.sectionRef) {
        handledSectionQueryKeyRef.current = `${payload.chapter_id}:${options.sectionRef}`;
        activateSection(options.sectionRef, payload, "section-click", {
          syncQuery: true,
          replaceQuery: false,
        });
      }
      setIsChapterSheetOpen(false);
      setMobileChapterSheetView("chapters");
      return;
    }
    setIsChapterSheetOpen(false);
    setMobileChapterSheetView("chapters");
    navigate(`${canonicalChapterPath(payload.book_id, chapterId)}${search}`);
  }

  function handleChapterPreview(chapter: ChapterListItem) {
    if (isMobile) {
      return;
    }
    if (hoverPreviewTimerRef.current != null) {
      window.clearTimeout(hoverPreviewTimerRef.current);
    }
    hoverPreviewTimerRef.current = window.setTimeout(() => {
      setPreviewChapterId(chapter.chapter_id);
      if (chapter.result_ready) {
        void ensureChapterOutline(chapter.chapter_id);
      }
    }, 110);
  }

  function openMobileChapterSections(chapter: ChapterListItem) {
    if (!chapter.result_ready) {
      return;
    }
    setPreviewChapterId(chapter.chapter_id);
    setMobileChapterSheetView("sections");
    void ensureChapterOutline(chapter.chapter_id);
  }

  function handleOutlineSectionClick(section: ChapterOutlineSectionItem) {
    if (!previewChapterId) {
      return;
    }
    if (previewChapterId === payload.chapter_id) {
      openChapter(previewChapterId, { sectionRef: section.section_ref });
      return;
    }
    openChapter(previewChapterId, { sectionRef: section.section_ref });
  }

  function renderNotesPane() {
    return (
      <div className="rc-scrollbar h-full overflow-y-auto bg-[var(--warm-100)]">
        <div className="sticky top-0 z-20 border-b border-[var(--warm-200)] bg-[var(--warm-50)]/95 backdrop-blur px-5 pt-5 pb-4 sm:px-6 lg:px-7">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div>
              <p className="text-[var(--warm-500)] uppercase tracking-[0.18em] mb-1" style={{ fontSize: "0.6875rem", fontWeight: 600 }}>
                Reading notes
              </p>
              <p className="text-[var(--warm-700)]" style={{ fontSize: "0.9rem", lineHeight: 1.6 }}>
                {payload.visible_reaction_count} notes grounded in this chapter
              </p>
            </div>
            <div className="text-right">
              <p className="text-[var(--warm-500)]" style={{ fontSize: "0.75rem" }}>
                {payload.high_signal_reaction_count} high-signal
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 mt-4">
            {renderedFilters.map((filter) => (
              <button
                key={filter}
                type="button"
                onClick={() => handleFilterChange(filter)}
                data-testid={`reaction-filter-${filter}`}
                className={activeFilter === filter ? filterActiveClass : filterInactiveClass}
                style={{ fontSize: "0.75rem", fontWeight: 600 }}
              >
                {filter === "all" ? "All" : reactionLabel(filter)}
              </button>
            ))}
          </div>

          {sectionHint ? (
            <p className="mt-3 text-[var(--amber-accent)]" style={{ fontSize: "0.75rem", lineHeight: 1.55, fontWeight: 500 }}>
              {sectionHint}
            </p>
          ) : null}
        </div>

        <div className="px-5 pb-6 pt-5 sm:px-6 lg:px-7">
          <div className="space-y-8">
            {visibleSections.length === 0 ? (
              <div className="rounded-2xl border border-[var(--warm-300)]/40 bg-white px-4 py-6">
                <p className="text-[var(--warm-800)]" style={{ fontSize: "0.9rem", fontWeight: 600 }}>
                  No reactions under this filter.
                </p>
                <p className="text-[var(--warm-600)] mt-1" style={{ fontSize: "0.82rem", lineHeight: 1.7 }}>
                  Switch back to All to continue linked reading and jump navigation.
                </p>
              </div>
            ) : null}

            {visibleSections.map((section) => (
              <section
                key={section.section_ref}
                ref={(node) => {
                  sectionRefs.current.set(section.section_ref, node);
                }}
                className={`rounded-2xl transition-colors ${
                  passiveSectionRef === section.section_ref
                    ? "bg-[var(--amber-bg)]/45 border border-[var(--amber-accent)]/20 p-3 -m-3"
                    : ""
                }`}
                style={{ scrollMarginTop: "1.25rem" }}
              >
                <div className="mb-3 pb-2 border-b border-[var(--warm-200)]">
                  <div className="flex items-center justify-between gap-3 flex-wrap">
                    <div>
                      <p className="text-[var(--amber-accent)] mb-1" style={{ fontSize: "0.75rem", fontWeight: 600 }}>
                        {section.section_ref}
                      </p>
                      <p className="text-[var(--warm-900)]" style={{ fontSize: "1rem", fontWeight: 600, lineHeight: 1.45 }}>
                        {section.summary}
                      </p>
                    </div>
                    <div className="text-right">
                      {passiveSectionRef === section.section_ref ? (
                        <p className="text-[var(--amber-accent)]" style={{ fontSize: "0.72rem", fontWeight: 600 }}>
                          Reading here
                        </p>
                      ) : null}
                      {section.verdict ? (
                        <p className="text-[var(--warm-500)]" style={{ fontSize: "0.75rem" }}>
                          {section.verdict}
                        </p>
                      ) : null}
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  {section.reactions.map((reaction) => {
                    const isActive = activeReactionId === reaction.reaction_id;
                    const anchorQuote = reaction.anchor_quote.trim();
                    const reactionTone = reactionMeta[reaction.type];
                    return (
                      <article
                        key={reaction.reaction_id}
                        data-testid={`reaction-card-${reaction.reaction_id}`}
                        className={`rounded-2xl border p-4 cursor-pointer transition-colors ${
                          isActive
                            ? "border-[var(--amber-accent)]/45 bg-[var(--amber-bg)] shadow-[0_1px_0_rgba(255,255,255,0.9),0_20px_38px_rgba(139,105,20,0.11)]"
                            : "border-[var(--warm-300)]/30 bg-white shadow-[0_1px_0_rgba(255,255,255,0.92),0_12px_28px_rgba(61,46,31,0.04)] hover:-translate-y-[1px] hover:border-[var(--warm-300)]/65 hover:shadow-[0_1px_0_rgba(255,255,255,0.94),0_18px_34px_rgba(61,46,31,0.07)]"
                        }`}
                        style={{ transitionDuration: "180ms" }}
                        onClick={() => selectReaction(reaction.reaction_id, "note-click", payload)}
                      >
                        <div className="flex items-start justify-between gap-3 flex-wrap mb-3">
                          <div className="flex items-center gap-2">
                            <span
                              className={`${pillBaseClass} h-9 border-[var(--warm-300)]/45 ${reactionTone.surfaceClass} ${reactionTone.accentClass}`}
                              style={{ fontSize: "0.74rem", fontWeight: 600 }}
                            >
                              {reactionLabel(reaction.type)}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={(event) => {
                                event.stopPropagation();
                                void toggleMark(reaction.reaction_id, reaction.mark_type ?? null, "resonance");
                              }}
                              data-testid={`mark-resonance-${reaction.reaction_id}`}
                              className={`${markButtonBaseClass} ${
                                reaction.mark_type === "resonance"
                                  ? "border-[var(--amber-accent)]/35 bg-[var(--amber-bg)] text-[var(--amber-accent)] shadow-[0_1px_0_rgba(255,255,255,0.82),0_12px_28px_rgba(139,105,20,0.1)]"
                                  : ""
                              }`}
                              style={{ fontSize: "0.72rem", fontWeight: 600 }}
                            >
                              {markLabel("resonance")}
                            </button>
                            <button
                              type="button"
                              onClick={(event) => {
                                event.stopPropagation();
                                void toggleMark(reaction.reaction_id, reaction.mark_type ?? null, "blindspot");
                              }}
                              data-testid={`mark-blindspot-${reaction.reaction_id}`}
                              className={`${markButtonBaseClass} ${
                                reaction.mark_type === "blindspot"
                                  ? "border-orange-300/65 bg-orange-50 text-orange-700 shadow-[0_1px_0_rgba(255,255,255,0.82),0_12px_28px_rgba(234,88,12,0.08)]"
                                  : ""
                              }`}
                              style={{ fontSize: "0.72rem", fontWeight: 600 }}
                            >
                              {markLabel("blindspot")}
                            </button>
                            <button
                              type="button"
                              onClick={(event) => {
                                event.stopPropagation();
                                void toggleMark(reaction.reaction_id, reaction.mark_type ?? null, "bookmark");
                              }}
                              data-testid={`mark-bookmark-${reaction.reaction_id}`}
                              className={`${markButtonBaseClass} ${
                                reaction.mark_type === "bookmark"
                                  ? "border-emerald-300/65 bg-emerald-50 text-emerald-700 shadow-[0_1px_0_rgba(255,255,255,0.82),0_12px_28px_rgba(16,185,129,0.08)]"
                                  : ""
                              }`}
                              style={{ fontSize: "0.72rem", fontWeight: 600 }}
                            >
                              {markLabel("bookmark")}
                            </button>
                          </div>
                        </div>

                        {anchorQuote ? (
                          <blockquote
                            className="border-l-2 border-[var(--amber-accent)]/40 pl-4 mb-3 text-[var(--warm-600)] italic"
                            style={{ fontSize: "0.8125rem", lineHeight: 1.7 }}
                          >
                            “{anchorQuote}”
                          </blockquote>
                        ) : null}

                        {isActive ? (
                          <>
                            <p className="text-[var(--warm-800)]" style={{ fontSize: "0.875rem", lineHeight: 1.82 }}>
                              {reaction.content}
                            </p>
                            {reaction.search_results.length > 0 ? (
                              <section className="mt-4">
                                <div className="flex items-center gap-2 mb-2">
                                  <Search className="w-4 h-4 text-[var(--amber-accent)]" />
                                  <p className="text-[var(--warm-900)]" style={{ fontSize: "0.78rem", fontWeight: 600 }}>
                                    Extra context
                                  </p>
                                </div>
                                <div className="space-y-2">
                                  {reaction.search_results.map((result) => (
                                    <a
                                      key={result.url}
                                      href={result.url}
                                      target="_blank"
                                      rel="noreferrer"
                                      className="block rounded-xl bg-white/70 border border-[var(--warm-300)]/40 p-3 no-underline hover:bg-white transition-colors"
                                    >
                                      <p className="text-[var(--warm-900)] mb-1" style={{ fontSize: "0.77rem", fontWeight: 600 }}>
                                        {result.title}
                                      </p>
                                      <p className="text-[var(--warm-600)]" style={{ fontSize: "0.75rem", lineHeight: 1.65 }}>
                                        {result.snippet}
                                      </p>
                                    </a>
                                  ))}
                                </div>
                              </section>
                            ) : null}
                          </>
                        ) : (
                          <p className="text-[var(--warm-700)]" style={{ fontSize: "0.84rem", lineHeight: 1.75 }}>
                            {reactionPreview(reaction.content)}
                          </p>
                        )}
                      </article>
                    );
                  })}
                </div>
              </section>
            ))}
          </div>

        </div>
      </div>
    );
  }

  const sourceUrl = toApiAssetUrl(payload.source_asset.url);
  const readerBookTitle = (bookDetail?.title || "").trim() || payload.title || "Original book";

  return (
    <div className="h-[calc(100vh-72px)] flex flex-col bg-[var(--warm-100)]">
      <Sheet open={isChapterSheetOpen} onOpenChange={setIsChapterSheetOpen}>
        <SheetContent
          side="left"
          data-testid="chapter-sheet-content"
          className={`gap-0 border-[var(--warm-300)]/50 bg-[var(--warm-50)] p-0 text-[var(--warm-900)] ${
            isMobile
              ? "w-[100vw] max-w-[100vw]"
              : "w-[min(880px,calc(100vw-40px))] max-w-[min(880px,calc(100vw-40px))] sm:max-w-none"
          }`}
        >
          <SheetHeader className="border-b border-[var(--warm-200)] bg-[var(--warm-50)] px-5 py-5 pr-12">
            <SheetTitle
              className="font-['Lora',Georgia,serif] text-[var(--warm-950)]"
              style={{ fontSize: "1.25rem", lineHeight: 1.2 }}
            >
              {readerBookTitle}
            </SheetTitle>
            <SheetDescription
              className="text-[var(--warm-600)]"
              style={{ fontSize: "0.84rem", lineHeight: 1.6 }}
            >
              {chapterItems.length} chapters
            </SheetDescription>
          </SheetHeader>

          <div className={`min-h-0 flex-1 overflow-hidden ${isMobile ? "flex flex-col" : "grid grid-cols-[304px_minmax(0,1fr)]"}`}>
            <div className={`rc-scrollbar min-h-0 overflow-y-auto ${isMobile ? "flex-1 px-3 py-3" : "border-r border-[var(--warm-200)] bg-[var(--warm-100)]/78 px-3 py-3"}`}>
              {isMobile && mobileChapterSheetView === "sections" ? (
                <div className="mb-3 flex items-center gap-2 px-1">
                  <button
                    type="button"
                    onClick={() => setMobileChapterSheetView("chapters")}
                    className="inline-flex h-8 items-center gap-2 rounded-full border border-[var(--warm-300)]/65 bg-white/86 px-3 text-[var(--warm-700)] shadow-[0_1px_0_rgba(255,255,255,0.88)] transition-all duration-200 hover:bg-white"
                    style={{ fontSize: "0.76rem", fontWeight: 600 }}
                  >
                    <ArrowLeft className="h-3.5 w-3.5" />
                    Chapters
                  </button>
                </div>
              ) : null}

              {(!isMobile || mobileChapterSheetView === "chapters") ? (
                <div className="space-y-1.5">
                  {chapterItems.map((chapter) => {
                    const isCurrent = chapter.chapter_id === payload.chapter_id;
                    const chapterTitle =
                      chapter.title && chapter.title !== chapter.chapter_ref ? chapter.title : chapter.chapter_ref;
                    const chapterMeta =
                      chapter.title && chapter.title !== chapter.chapter_ref ? chapter.chapter_ref : null;
                    const StatusIcon = isCurrent
                      ? CheckCircle2
                      : !chapter.result_ready
                        ? chapter.status === "error"
                          ? AlertTriangle
                          : CircleDashed
                        : CheckCircle2;
                    const chapterStateLabel = isCurrent
                      ? "Current"
                      : !chapter.result_ready
                        ? chapter.status === "error"
                          ? "Error"
                          : "Pending"
                        : chapter.status === "error"
                          ? "Error"
                          : "Completed";
                    const isPreviewing = previewChapterId === chapter.chapter_id;

                    return (
                      <button
                        key={chapter.chapter_id}
                        type="button"
                        data-testid={`chapter-sheet-item-${chapter.chapter_id}`}
                        disabled={!chapter.result_ready && !isCurrent}
                        onMouseEnter={() => handleChapterPreview(chapter)}
                        onFocus={() => handleChapterPreview(chapter)}
                        onClick={() => {
                          if (isMobile) {
                            openMobileChapterSections(chapter);
                            return;
                          }
                          if (!chapter.result_ready || isCurrent) {
                            return;
                          }
                          openChapter(chapter.chapter_id);
                        }}
                        className={`w-full rounded-2xl border px-4 py-3 text-left transition-all duration-200 ${
                          isCurrent
                            ? "border-[var(--amber-accent)]/28 bg-[var(--amber-bg)]/85 shadow-[0_1px_0_rgba(255,255,255,0.88),0_18px_34px_rgba(139,105,20,0.09)]"
                            : isPreviewing
                              ? "border-[var(--warm-300)]/60 bg-white/92 shadow-[0_1px_0_rgba(255,255,255,0.9),0_14px_32px_rgba(61,46,31,0.06)]"
                              : chapter.result_ready
                                ? "border-[var(--warm-300)]/28 bg-white/72 hover:-translate-y-[1px] hover:border-[var(--warm-400)]/55 hover:bg-white"
                                : "cursor-not-allowed border-[var(--warm-300)]/20 bg-[var(--warm-100)]/70 opacity-80"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            {chapterMeta ? (
                              <p
                                className="mb-1 text-[var(--warm-500)]"
                                style={{ fontSize: "0.69rem", fontWeight: 600, lineHeight: 1.3 }}
                              >
                                {chapterMeta}
                              </p>
                            ) : null}
                            <OverflowTooltipText
                              as="p"
                              text={chapterTitle}
                              lines={2}
                              side="right"
                              className="text-[var(--warm-950)]"
                              style={{ fontSize: "0.9rem", fontWeight: 600, lineHeight: 1.45, maxWidth: "14.25rem" }}
                            />
                            <p
                              className="mt-1 text-[var(--warm-600)]"
                              style={{ fontSize: "0.74rem", lineHeight: 1.55 }}
                            >
                              {chapter.visible_reaction_count} reactions · {chapter.high_signal_reaction_count} high-signal
                            </p>
                          </div>

                          <div className="flex shrink-0 items-center gap-2">
                            <span
                              className={`inline-flex rounded-full border px-2.5 py-1 ${
                                isCurrent
                                  ? "border-[var(--amber-accent)]/30 bg-white/78 text-[var(--amber-accent)]"
                                  : chapter.result_ready
                                    ? "border-[var(--warm-300)]/45 bg-[var(--warm-50)] text-[var(--warm-600)]"
                                    : chapter.status === "error"
                                      ? "border-red-200 bg-red-50 text-red-700"
                                      : "border-[var(--warm-300)]/40 bg-[var(--warm-50)] text-[var(--warm-500)]"
                              }`}
                              style={{ fontSize: "0.69rem", fontWeight: 600 }}
                            >
                              <StatusIcon className="mr-1 h-3 w-3" />
                              {chapterStateLabel}
                            </span>
                            {(chapter.result_ready && !isCurrent) || (isMobile && chapter.result_ready) ? (
                              <ChevronRight className="h-4 w-4 text-[var(--warm-400)]" />
                            ) : null}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              ) : null}

              {isMobile && mobileChapterSheetView === "sections" ? (
                previewOutlineLoading ? (
                  <div className="flex min-h-[14rem] items-center justify-center">
                    <p className="inline-flex items-center gap-2 text-[var(--warm-600)]" style={{ fontSize: "0.82rem" }}>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Loading chapter outline...
                    </p>
                  </div>
                ) : !previewChapter?.result_ready ? (
                  <div className="rounded-2xl border border-[var(--warm-300)]/35 bg-[var(--warm-50)]/78 px-4 py-5">
                    <p className="text-[var(--warm-900)]" style={{ fontSize: "0.88rem", fontWeight: 600 }}>
                      This chapter is not ready yet.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {(previewOutline?.sections ?? []).map((section) => {
                      const isCurrentSection =
                        previewChapterId === payload.chapter_id && currentReadingSectionRef === section.section_ref;
                      return (
                        <button
                          key={section.section_ref}
                          type="button"
                          onClick={() => handleOutlineSectionClick(section)}
                          className={`w-full rounded-2xl border px-4 py-3 text-left transition-all duration-200 ${
                            isCurrentSection
                              ? "border-[var(--amber-accent)]/28 bg-[var(--amber-bg)]/82"
                              : "border-[var(--warm-300)]/28 bg-white/86 hover:-translate-y-[1px] hover:border-[var(--warm-400)]/55 hover:bg-white"
                          }`}
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div className="min-w-0">
                              <p className="text-[var(--amber-accent)]" style={{ fontSize: "0.7rem", fontWeight: 600 }}>
                                {section.section_ref}
                              </p>
                              <OverflowTooltipText
                                as="p"
                                text={section.summary}
                                lines={2}
                                side="right"
                                className="mt-1 text-[var(--warm-950)]"
                                style={{ fontSize: "0.9rem", fontWeight: 600, lineHeight: 1.45 }}
                              />
                              {section.preview_text ? (
                                <p className="mt-1 text-[var(--warm-600)]" style={{ fontSize: "0.76rem", lineHeight: 1.55 }}>
                                  {section.preview_text}
                                </p>
                              ) : null}
                            </div>
                            <div className="shrink-0 text-right">
                              <p className="text-[var(--warm-500)]" style={{ fontSize: "0.7rem", fontWeight: 600 }}>
                                {section.visible_reaction_count}
                              </p>
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )
              ) : null}
            </div>

            {!isMobile ? (
              <div className="min-h-0 overflow-hidden bg-white/68">
                <div className="border-b border-[var(--warm-200)] bg-[var(--warm-50)]/94 px-5 py-4">
                  <p className="text-[var(--warm-500)] uppercase tracking-[0.16em]" style={{ fontSize: "0.64rem", fontWeight: 600 }}>
                    In this chapter
                  </p>
                  <div className="mt-1 flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <OverflowTooltipText
                        as="p"
                        text={previewOutline?.title || previewChapter?.title || previewChapter?.chapter_ref || "Chapter preview"}
                        lines={1}
                        side="bottom"
                        className="text-[var(--warm-950)] font-['Lora',Georgia,serif]"
                        style={{ fontSize: "1.02rem", fontWeight: 700, lineHeight: 1.25, maxWidth: "26rem" }}
                      />
                      <p className="mt-1 text-[var(--warm-600)]" style={{ fontSize: "0.76rem", lineHeight: 1.5 }}>
                        {(previewOutline?.section_count ?? previewChapter?.segment_count ?? 0)} sections
                      </p>
                    </div>
                    {previewChapter?.chapter_ref ? (
                      <span className="inline-flex h-8 items-center rounded-full border border-[var(--warm-300)]/68 bg-white/84 px-3 text-[var(--warm-700)] shadow-[0_1px_0_rgba(255,255,255,0.88)]" style={{ fontSize: "0.72rem", fontWeight: 600 }}>
                        {previewChapter.chapter_ref}
                      </span>
                    ) : null}
                  </div>
                </div>

                <div className="rc-scrollbar h-full overflow-y-auto px-4 py-4">
                  {previewOutlineLoading ? (
                    <div className="flex h-full min-h-[16rem] items-center justify-center">
                      <p className="inline-flex items-center gap-2 text-[var(--warm-600)]" style={{ fontSize: "0.82rem" }}>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Loading chapter outline...
                      </p>
                    </div>
                  ) : !previewChapter?.result_ready ? (
                    <div className="rounded-2xl border border-[var(--warm-300)]/35 bg-[var(--warm-50)]/78 px-4 py-5">
                      <p className="text-[var(--warm-900)]" style={{ fontSize: "0.88rem", fontWeight: 600 }}>
                        This chapter is not ready yet.
                      </p>
                      <p className="mt-1 text-[var(--warm-600)]" style={{ fontSize: "0.78rem", lineHeight: 1.65 }}>
                        Finish analysis in the book overview before using section-level navigation here.
                      </p>
                    </div>
                  ) : previewSectionItems.length === 0 ? (
                    <div className="rounded-2xl border border-[var(--warm-300)]/35 bg-[var(--warm-50)]/78 px-4 py-5">
                      <p className="text-[var(--warm-900)]" style={{ fontSize: "0.88rem", fontWeight: 600 }}>
                        No semantic sections available.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {previewSectionItems.map((section) => {
                        const isCurrentSection =
                          previewChapterId === payload.chapter_id && currentReadingSectionRef === section.section_ref;
                        return (
                          <button
                            key={section.section_ref}
                            type="button"
                            data-testid={`chapter-outline-section-${previewChapterId}-${section.section_ref}`}
                            onClick={() => handleOutlineSectionClick(section)}
                            className={`w-full rounded-2xl border px-4 py-3 text-left transition-all duration-200 ${
                              isCurrentSection
                                ? "border-[var(--amber-accent)]/28 bg-[var(--amber-bg)]/78 shadow-[0_1px_0_rgba(255,255,255,0.88),0_14px_30px_rgba(139,105,20,0.08)]"
                                : "border-[var(--warm-300)]/26 bg-white/88 hover:-translate-y-[1px] hover:border-[var(--warm-400)]/55 hover:bg-white"
                            }`}
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div className="min-w-0">
                                <p className="text-[var(--amber-accent)]" style={{ fontSize: "0.7rem", fontWeight: 600 }}>
                                  {section.section_ref}
                                </p>
                                <OverflowTooltipText
                                  as="p"
                                  text={section.summary}
                                  lines={2}
                                  side="right"
                                  className="mt-1 text-[var(--warm-950)]"
                                  style={{ fontSize: "0.88rem", fontWeight: 600, lineHeight: 1.42 }}
                                />
                                {section.preview_text ? (
                                  <p className="mt-1.5 text-[var(--warm-600)]" style={{ fontSize: "0.77rem", lineHeight: 1.6 }}>
                                    {section.preview_text}
                                  </p>
                                ) : null}
                              </div>
                              <div className="shrink-0 text-right">
                                {isCurrentSection ? (
                                  <p className="text-[var(--amber-accent)]" style={{ fontSize: "0.68rem", fontWeight: 600 }}>
                                    Reading
                                  </p>
                                ) : null}
                                <p className="mt-1 text-[var(--warm-500)]" style={{ fontSize: "0.7rem", fontWeight: 600 }}>
                                  {section.visible_reaction_count} notes
                                </p>
                              </div>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            ) : null}
          </div>

          <SheetFooter className="border-t border-[var(--warm-200)] bg-[var(--warm-50)] px-5 py-4">
            <Link
              to={canonicalBookPath(payload.book_id)}
              data-testid="chapter-sheet-book-overview-link"
              className="inline-flex h-10 items-center justify-center gap-2 rounded-full border border-[var(--warm-300)]/60 bg-white/84 px-4 text-[var(--warm-600)] no-underline shadow-[0_1px_0_rgba(255,255,255,0.88),0_10px_24px_rgba(61,46,31,0.04)] transition-all duration-200 hover:-translate-y-[1px] hover:border-[var(--warm-400)] hover:bg-white hover:text-[var(--warm-900)]"
              style={{ fontSize: "0.82rem", fontWeight: 600 }}
            >
              Open book overview
            </Link>
          </SheetFooter>
        </SheetContent>

      <div className="border-b border-[var(--warm-200)] bg-[var(--warm-50)]/95 backdrop-blur-sm flex-shrink-0">
        <div className="px-5 py-2.5 sm:px-6 lg:px-7">
          <div className="flex flex-wrap items-start justify-between gap-3 lg:flex-nowrap lg:gap-6">
            <div className="min-w-0 flex-1">
              <OverflowTooltipText
                as="p"
                text={readerBookTitle}
                lines={1}
                side="bottom"
                className="text-[var(--warm-600)]"
                style={{
                  fontSize: "0.82rem",
                  fontWeight: 600,
                  lineHeight: 1.35,
                  maxWidth: "min(56rem, 100%)",
                }}
              />

              <div className="mt-1.5 flex min-w-0 items-center gap-2.5 flex-wrap">
                {showSeparateChapterTitle ? (
                  <span
                    className="inline-flex h-7 items-center rounded-full border border-[var(--warm-300)]/65 bg-white/78 px-3 text-[var(--warm-700)] shadow-[0_1px_0_rgba(255,255,255,0.88)]"
                    style={{ fontSize: "0.74rem", fontWeight: 600 }}
                    data-testid="chapter-workspace-current-chapter"
                  >
                    {currentChapterRef}
                  </span>
                ) : null}
                <OverflowTooltipText
                  as="h1"
                  text={workspaceHeading}
                  lines={1}
                  side="bottom"
                  data-testid={!showSeparateChapterTitle ? "chapter-workspace-current-chapter" : undefined}
                  className="min-w-0 text-[var(--warm-950)] font-['Lora',Georgia,serif] tracking-tight"
                  style={{
                    fontSize: "clamp(1.04rem, 1.25vw, 1.26rem)",
                    fontWeight: 700,
                    lineHeight: 1.14,
                    maxWidth: "min(40rem, 100%)",
                  }}
                />
              </div>
            </div>

            <div className="flex shrink-0 items-center gap-2 flex-wrap lg:justify-end">
              {showChapterSwitcher ? (
                <SheetTrigger asChild>
                  <button
                    type="button"
                    data-testid="chapter-sheet-trigger"
                    className={workspacePrimaryActionClass}
                    style={{ fontSize: "0.76rem", fontWeight: 600 }}
                  >
                    <List className="h-4 w-4" />
                    Chapters
                  </button>
                </SheetTrigger>
              ) : null}
              <Link
                to={canonicalBookPath(payload.book_id)}
                className={`${workspaceSecondaryActionClass} no-underline text-[var(--warm-600)]`}
                style={{ fontSize: "0.76rem", fontWeight: 600 }}
              >
                <ArrowLeft className="h-4 w-4" />
                Overview
              </Link>
            </div>
          </div>
        </div>
      </div>

      {error ? (
        <div className="px-6 pt-4">
          <p className="text-[var(--destructive)]" style={{ fontSize: "0.8125rem" }}>
            {error}
          </p>
        </div>
      ) : null}

      <div className="flex-1 overflow-hidden bg-[var(--warm-100)]">
        {isMobile ? (
          <Tabs
            value={mobileMode}
            onValueChange={(next) => setMobileMode(next as ReaderPanelMode)}
            className="h-full"
          >
            <div className="px-4 py-2 border-b border-[var(--warm-200)]">
              <TabsList className="w-full max-w-xs">
                <TabsTrigger value="notes">Notes</TabsTrigger>
                <TabsTrigger value="book">Original book</TabsTrigger>
              </TabsList>
            </div>
            <TabsContent value="notes" className="h-[calc(100%-58px)]">
              {renderNotesPane()}
            </TabsContent>
            <TabsContent value="book" className="h-[calc(100%-58px)]">
              <SourceReaderPane
                sourceUrl={sourceUrl}
                chapterRef={payload.chapter_ref}
                chapterTitle={payload.title}
                sections={payload.sections}
                jumpRequest={jumpRequest}
                followNotes={followNotes}
                onFollowNotesChange={setFollowNotes}
                onLocationChange={(update: ReaderLocationUpdate) => {
                  if (!followNotes || update.programmatic) {
                    return;
                  }
                  setPassiveSectionRef(update.location.sectionRef);
                }}
              />
            </TabsContent>
          </Tabs>
        ) : (
          <ResizablePanelGroup
            direction="horizontal"
            autoSaveId={`chapter-workspace:${payload.book_id}:${chapterNumber}`}
            className="h-full bg-[var(--warm-100)]"
          >
            <ResizablePanel defaultSize={45} minSize={28} className="bg-[var(--warm-100)]">
              {renderNotesPane()}
            </ResizablePanel>
            <ResizableHandle withHandle />
            <ResizablePanel defaultSize={55} minSize={35} className="bg-[var(--warm-100)]">
              <SourceReaderPane
                sourceUrl={sourceUrl}
                chapterRef={payload.chapter_ref}
                chapterTitle={payload.title}
                sections={payload.sections}
                jumpRequest={jumpRequest}
                followNotes={followNotes}
                onFollowNotesChange={setFollowNotes}
                onLocationChange={(update: ReaderLocationUpdate) => {
                  if (!followNotes || update.programmatic) {
                    return;
                  }
                  setPassiveSectionRef(update.location.sectionRef);
                }}
              />
            </ResizablePanel>
          </ResizablePanelGroup>
        )}
      </div>
      </Sheet>
    </div>
  );
}
