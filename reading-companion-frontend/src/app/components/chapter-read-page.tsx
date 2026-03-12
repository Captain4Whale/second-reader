import { ArrowLeft, ChevronRight, List, Search } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router";
import {
  BookDetailResponse,
  ChapterDetailResponse,
  deleteReactionMark,
  fetchBookDetail,
  fetchChapterDetail,
  putReactionMark,
  toApiAssetUrl,
} from "../lib/api";
import type { SectionCard } from "../lib/api-types";
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
  buildReaderJumpRequest,
  findSelectionByReactionId,
  reactionPreview,
  type ReaderJumpRequest,
  type ReaderLocationUpdate,
  type ReaderPanelMode,
} from "../lib/reader-types";
import { reactionLabel } from "../lib/reactions";
import { ErrorState, LoadingState } from "./page-state";
import { SourceReaderPane } from "./source-reader-pane";
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

function readFollowNotesPreference(): boolean {
  if (typeof window === "undefined") {
    return true;
  }
  return window.localStorage.getItem(FOLLOW_NOTES_STORAGE_KEY) !== "off";
}

function chapterFilterStorageKey(bookId: string): string {
  return `${CHAPTER_FILTER_STORAGE_KEY_PREFIX}:${bookId}`;
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
  const [mobileMode, setMobileMode] = useState<ReaderPanelMode>("notes");
  const [followNotes, setFollowNotes] = useState(readFollowNotesPreference);
  const [passiveSectionRef, setPassiveSectionRef] = useState<string | null>(null);
  const [jumpRequest, setJumpRequest] = useState<ReaderJumpRequest | null>(null);
  const [isChapterSheetOpen, setIsChapterSheetOpen] = useState(false);

  const jumpSequenceRef = useRef(0);
  const lastNoteJumpAtRef = useRef(0);
  const queryReactionId = useMemo(() => parseReactionSearch(location.search), [location.search]);

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

  const syncReactionQuery = useCallback(
    (reactionId: ReactionId | null, replace = false) => {
      const params = new URLSearchParams(location.search);
      if (reactionId == null) {
        params.delete("reaction");
      } else {
        params.set("reaction", String(reactionId));
      }
      const search = params.toString();
      const target = `${location.pathname}${search ? `?${search}` : ""}`;
      const current = `${location.pathname}${location.search}`;
      if (target === current) {
        return;
      }
      navigate(target, { replace });
    },
    [location.pathname, location.search, navigate],
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
    setActiveFilter(readChapterFilterPreference(resolvedBookId));
  }, [resolvedBookId]);

  useEffect(() => {
    if (typeof window === "undefined" || !resolvedBookId) {
      return;
    }
    window.sessionStorage.setItem(chapterFilterStorageKey(resolvedBookId), activeFilter);
  }, [activeFilter, resolvedBookId]);

  useEffect(() => {
    setIsChapterSheetOpen(false);
  }, [chapterNumber]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    void Promise.all([
      fetchChapterDetail(bookIdNumber, chapterNumber),
      fetchBookDetail(bookIdNumber).catch(() => null),
    ])
      .then(([nextPayload, nextBookDetail]) => {
        if (!active) {
          return;
        }

        setPayload(nextPayload);
        setBookDetail(nextBookDetail);
        const initialReactionId =
          (queryReactionId != null && findSelectionByReactionId(nextPayload.sections, queryReactionId)
            ? queryReactionId
            : null) ??
          initialReactionIdForFilter(nextPayload.sections, activeFilter) ??
          null;

        setActiveReactionId(initialReactionId);
        if (initialReactionId != null) {
          queueReaderJump(
            initialReactionId,
            queryReactionId != null ? "deep-link" : "initial",
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
  }, [bookIdNumber, chapterNumber, queryReactionId, queueReaderJump, reloadTick]);

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
  const pillBaseClass = "inline-flex h-8 items-center rounded-full border px-3 transition-colors";
  const filterInactiveClass = `${pillBaseClass} border-[var(--warm-300)]/60 text-[var(--warm-600)] hover:bg-[var(--warm-100)]`;
  const filterActiveClass = `${pillBaseClass} border-[var(--amber-accent)] bg-[var(--amber-bg)] text-[var(--amber-accent)]`;
  const markButtonBaseClass = `${pillBaseClass} text-[var(--warm-600)]`;
  const chapterItems = bookDetail?.chapters ?? [];
  const readableChapterCount = chapterItems.filter((chapter) => chapter.result_ready).length;
  const showChapterSwitcher = Boolean(bookDetail) && readableChapterCount > 1;

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

  function openChapter(chapterId: number) {
    if (chapterId === payload.chapter_id) {
      setIsChapterSheetOpen(false);
      return;
    }
    setIsChapterSheetOpen(false);
    navigate(canonicalChapterPath(payload.book_id, chapterId));
  }

  function renderNotesPane() {
    return (
      <div className="h-full overflow-y-auto bg-[var(--warm-100)]">
        <div className="sticky top-0 z-20 border-b border-[var(--warm-200)] bg-[var(--warm-50)]/95 backdrop-blur px-6 pt-6 pb-4">
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
                onClick={() => setActiveFilter(filter)}
                data-testid={`reaction-filter-${filter}`}
                className={activeFilter === filter ? filterActiveClass : filterInactiveClass}
                style={{ fontSize: "0.75rem", fontWeight: 600 }}
              >
                {filter === "all" ? "All" : reactionLabel(filter)}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6 pt-5">
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
                className={`rounded-2xl transition-colors ${
                  passiveSectionRef === section.section_ref
                    ? "bg-[var(--amber-bg)]/45 border border-[var(--amber-accent)]/20 p-3 -m-3"
                    : ""
                }`}
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
                    return (
                      <article
                        key={reaction.reaction_id}
                        data-testid={`reaction-card-${reaction.reaction_id}`}
                        className={`rounded-2xl border p-4 cursor-pointer transition-colors ${
                          isActive
                            ? "border-[var(--amber-accent)]/45 bg-[var(--amber-bg)]"
                            : "border-[var(--warm-300)]/30 bg-white hover:border-[var(--warm-300)]"
                        }`}
                        onClick={() => selectReaction(reaction.reaction_id, "note-click", payload)}
                      >
                        <div className="flex items-start justify-between gap-3 flex-wrap mb-3">
                          <div className="flex items-center gap-2">
                            <span
                              className={`${pillBaseClass} border-[var(--warm-300)]/60 bg-[var(--warm-100)] text-[var(--warm-800)]`}
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
                                  ? "border-[var(--amber-accent)] bg-[var(--amber-bg)] text-[var(--amber-accent)]"
                                  : "border-[var(--warm-300)]/60 bg-white"
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
                                  ? "border-orange-300 bg-orange-50 text-orange-700"
                                  : "border-[var(--warm-300)]/60 bg-white"
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
                                  ? "border-emerald-300 bg-emerald-50 text-emerald-700"
                                  : "border-[var(--warm-300)]/60 bg-white"
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
  const chapterMetaLabel =
    payload.chapter_ref && payload.title && payload.chapter_ref !== payload.title
      ? `${payload.chapter_ref} · ${payload.title}`
      : payload.title || payload.chapter_ref;

  return (
    <div className="h-[calc(100vh-72px)] flex flex-col bg-[var(--warm-100)]">
      <Sheet open={isChapterSheetOpen} onOpenChange={setIsChapterSheetOpen}>
        <SheetContent
          side="left"
          data-testid="chapter-sheet-content"
          className="w-[24rem] max-w-[88vw] gap-0 border-[var(--warm-300)]/50 bg-[var(--warm-50)] p-0 text-[var(--warm-900)]"
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

          <div className="min-h-0 flex-1 overflow-y-auto px-3 py-3">
            <div className="space-y-2">
              {chapterItems.map((chapter) => {
                const isCurrent = chapter.chapter_id === payload.chapter_id;
                const isDisabled = !chapter.result_ready || isCurrent;
                const chapterTitle =
                  chapter.title && chapter.title !== chapter.chapter_ref ? chapter.title : chapter.chapter_ref;
                const chapterMeta =
                  chapter.title && chapter.title !== chapter.chapter_ref ? chapter.chapter_ref : null;
                const chapterStateLabel = isCurrent
                  ? "Current"
                  : !chapter.result_ready
                    ? chapter.status === "error"
                      ? "Error"
                      : "Pending"
                    : chapter.status === "error"
                      ? "Error"
                      : "Completed";

                return (
                  <button
                    key={chapter.chapter_id}
                    type="button"
                    data-testid={`chapter-sheet-item-${chapter.chapter_id}`}
                    disabled={isDisabled}
                    onClick={() => openChapter(chapter.chapter_id)}
                    className={`w-full rounded-2xl border px-4 py-3 text-left transition-colors ${
                      isCurrent
                        ? "cursor-default border-[var(--amber-accent)]/30 bg-[var(--amber-bg)]"
                        : chapter.result_ready
                          ? "border-[var(--warm-300)]/35 bg-white hover:border-[var(--amber-accent)]/35 hover:bg-[var(--warm-100)]/70"
                          : "cursor-not-allowed border-[var(--warm-300)]/25 bg-[var(--warm-100)]/75 opacity-80"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        {chapterMeta ? (
                          <p
                            className="mb-1 text-[var(--warm-500)]"
                            style={{ fontSize: "0.72rem", fontWeight: 600, lineHeight: 1.3 }}
                          >
                            {chapterMeta}
                          </p>
                        ) : null}
                        <p
                          className="text-[var(--warm-950)]"
                          style={{ fontSize: "0.94rem", fontWeight: 600, lineHeight: 1.45 }}
                        >
                          {chapterTitle}
                        </p>
                        {chapter.result_ready ? (
                          <p
                            className="mt-1 text-[var(--warm-600)]"
                            style={{ fontSize: "0.76rem", lineHeight: 1.55 }}
                          >
                            {chapter.visible_reaction_count} reactions · {chapter.high_signal_reaction_count} high-signal
                          </p>
                        ) : null}
                      </div>
                      <div className="flex flex-col items-end gap-2 shrink-0">
                        <span
                          className={`inline-flex rounded-full border px-2.5 py-1 ${
                            isCurrent
                              ? "border-[var(--amber-accent)]/30 bg-white/70 text-[var(--amber-accent)]"
                              : chapter.result_ready
                                ? "border-[var(--warm-300)]/40 bg-[var(--warm-50)] text-[var(--warm-600)]"
                                : chapter.status === "error"
                                  ? "border-red-200 bg-red-50 text-red-700"
                                  : "border-[var(--warm-300)]/40 bg-[var(--warm-50)] text-[var(--warm-500)]"
                          }`}
                          style={{ fontSize: "0.7rem", fontWeight: 600 }}
                        >
                          {chapterStateLabel}
                        </span>
                        {!isDisabled ? (
                          <ChevronRight className="h-4 w-4 text-[var(--warm-400)]" />
                        ) : null}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <SheetFooter className="border-t border-[var(--warm-200)] bg-[var(--warm-50)] px-5 py-4">
            <Link
              to={canonicalBookPath(payload.book_id)}
              data-testid="chapter-sheet-book-overview-link"
              className="inline-flex items-center gap-2 text-[var(--warm-600)] no-underline hover:text-[var(--warm-900)]"
              style={{ fontSize: "0.82rem", fontWeight: 600 }}
            >
              Open book overview
            </Link>
          </SheetFooter>
        </SheetContent>

      <div className="border-b border-[var(--warm-200)] bg-[var(--warm-50)]/95 backdrop-blur-sm flex-shrink-0">
        <div className="px-6 py-4">
          <Link
            to={canonicalBookPath(payload.book_id)}
            className="inline-flex items-center gap-1.5 text-[var(--warm-600)] no-underline hover:text-[var(--warm-800)]"
            style={{ fontSize: "0.84rem", fontWeight: 600 }}
          >
            <ArrowLeft className="w-4 h-4" />
            Back to book
          </Link>

          <div className="mt-3 min-w-0">
            <h1
              className="text-[var(--warm-950)] font-['Lora',Georgia,serif] tracking-tight overflow-hidden"
              style={{
                fontSize: "clamp(1.65rem, 2.7vw, 2.5rem)",
                fontWeight: 700,
                lineHeight: 1.08,
                maxWidth: "min(68rem, 100%)",
                display: "-webkit-box",
                WebkitBoxOrient: "vertical",
                WebkitLineClamp: 2,
              }}
            >
              {readerBookTitle}
            </h1>
            <div className="mt-1.5 flex items-center justify-between gap-3 flex-wrap">
              <p
                className="text-[var(--warm-600)]"
                style={{ fontSize: "1.02rem", lineHeight: 1.45, fontWeight: 500 }}
                data-testid="chapter-workspace-current-chapter"
              >
                {chapterMetaLabel}
              </p>
              {showChapterSwitcher ? (
                <SheetTrigger asChild>
                  <button
                    type="button"
                    data-testid="chapter-sheet-trigger"
                    className="inline-flex h-9 items-center gap-2 rounded-full border border-[var(--warm-300)]/60 bg-white/80 px-4 text-[var(--warm-700)] transition-colors hover:bg-[var(--warm-100)] hover:text-[var(--warm-900)]"
                    style={{ fontSize: "0.82rem", fontWeight: 600 }}
                  >
                    <List className="h-4 w-4" />
                    Chapters
                  </button>
                </SheetTrigger>
              ) : null}
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
