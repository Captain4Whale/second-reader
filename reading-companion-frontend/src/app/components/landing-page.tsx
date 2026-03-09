import { ArrowRight, Bookmark, Link2, RotateCcw, Scale, Search, Sparkles, Upload } from "lucide-react";
import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { Link } from "react-router";
import {
  LANDING_FOOTER_COPY,
  LANDING_HERO,
  LANDING_PREVIEW_CONFIG,
  LANDING_PREVIEW_SECTION,
  LANDING_REACTION_CARDS,
  LANDING_REACTION_SECTION,
  LANDING_SAMPLE_TEASERS,
} from "../content/landing-content";
import { type BookDetailResponse, type ChapterDetailResponse, fetchBookDetail, fetchChapterDetail } from "../lib/api";
import { canonicalBookPath, type ReactionType } from "../lib/contract";
import { reactionMeta } from "../lib/reactions";

const landingIcons = {
  highlight: Sparkles,
  association: Link2,
  discern: Scale,
  retrospect: RotateCcw,
  curious: Search,
  marks: Bookmark,
} as const;

type PreviewReaction = {
  reactionId: number;
  type: ReactionType;
  chapterRef: string;
  sectionRef: string;
  anchorQuote: string;
  content: string;
};

type ResolvedLandingPreview = {
  sourceTitle: string;
  sourceAuthor: string;
  sourceLabel: string;
  ctaTo: string;
  items: ReadonlyArray<PreviewReaction>;
};

function buildStaticPreview(): ResolvedLandingPreview {
  return {
    sourceTitle: LANDING_PREVIEW_CONFIG.static.sourceTitle,
    sourceAuthor: LANDING_PREVIEW_CONFIG.static.sourceAuthor,
    sourceLabel: LANDING_PREVIEW_CONFIG.static.sourceLabel,
    ctaTo: LANDING_PREVIEW_CONFIG.static.ctaTo,
    items: LANDING_PREVIEW_CONFIG.static.items,
  };
}

function selectPreviewItems(chapter: ChapterDetailResponse, maxItems: number) {
  const featured = chapter.featured_reactions.slice(0, maxItems).map((reaction) => ({
    reactionId: reaction.reaction_id,
    type: reaction.type,
    chapterRef: reaction.chapter_ref,
    sectionRef: reaction.section_ref,
    anchorQuote: reaction.anchor_quote,
    content: reaction.content,
  }));
  if (featured.length > 0) {
    return featured;
  }
  return chapter.sections
    .flatMap((section) =>
      section.reactions.map((reaction) => ({
        reactionId: reaction.reaction_id,
        type: reaction.type,
        chapterRef: chapter.chapter_ref,
        sectionRef: reaction.section_ref,
        anchorQuote: reaction.anchor_quote,
        content: reaction.content,
      })),
    )
    .slice(0, maxItems);
}

async function loadApiPreview(): Promise<ResolvedLandingPreview | null> {
  if (LANDING_PREVIEW_CONFIG.mode !== "api") {
    return null;
  }

  const detail: BookDetailResponse = await fetchBookDetail(LANDING_PREVIEW_CONFIG.api.bookId);
  const fallbackChapter = detail.chapters.find((chapter) => chapter.result_ready);
  const chapterId = LANDING_PREVIEW_CONFIG.api.chapterId ?? fallbackChapter?.chapter_id;

  if (!chapterId) {
    return null;
  }

  const chapter = await fetchChapterDetail(LANDING_PREVIEW_CONFIG.api.bookId, chapterId);
  const items = selectPreviewItems(chapter, LANDING_PREVIEW_CONFIG.api.maxItems);
  if (items.length === 0) {
    return null;
  }

  return {
    sourceTitle: detail.title,
    sourceAuthor: detail.author,
    sourceLabel: "From",
    ctaTo: LANDING_PREVIEW_CONFIG.api.ctaTo ?? canonicalBookPath(detail.book_id),
    items,
  };
}

export function LandingPage() {
  const [preview, setPreview] = useState<ResolvedLandingPreview>(buildStaticPreview);

  useEffect(() => {
    let active = true;
    setPreview(buildStaticPreview());

    if (LANDING_PREVIEW_CONFIG.mode !== "api") {
      return () => {
        active = false;
      };
    }

    void loadApiPreview()
      .then((nextPreview) => {
        if (!active || !nextPreview) {
          return;
        }
        setPreview(nextPreview);
      })
      .catch(() => undefined);

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="overflow-hidden">
      <section className="relative isolate px-6 pt-18 pb-24 md:pt-24 md:pb-30">
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute left-1/2 top-8 h-64 w-64 -translate-x-1/2 rounded-full bg-[var(--amber-accent)]/8 blur-3xl" />
          <div className="absolute -right-24 top-20 hidden xl:block h-96 w-96 rounded-full bg-[var(--association-color)] blur-3xl opacity-60" />
          <div className="absolute right-24 top-48 hidden xl:block h-72 w-72 rounded-full bg-[var(--retrospect-color)] blur-3xl opacity-50" />
          <div className="absolute left-16 bottom-10 hidden xl:block h-56 w-56 rounded-full bg-[var(--highlight-color)] blur-3xl opacity-60" />
        </div>

        <div className="pointer-events-none absolute right-16 top-28 hidden xl:flex w-[26rem] flex-col gap-4">
          {preview.items.slice(0, 2).map((reaction, index) => (
            <div
              key={reaction.reactionId}
              className={`rounded-[28px] border border-[var(--warm-300)]/35 bg-white/88 p-5 shadow-[0_24px_80px_rgba(68,42,28,0.10)] backdrop-blur-sm ${
                index === 0 ? "translate-x-0 rotate-[-3deg]" : "translate-x-12 rotate-[4deg]"
              }`}
            >
              <div className="mb-3 flex items-center justify-between gap-3">
                <span
                  className={`inline-flex items-center rounded-full px-2.5 py-1 text-[0.75rem] font-medium text-[var(--warm-900)] ${reactionMeta[reaction.type].surfaceClass}`}
                >
                  {reactionMeta[reaction.type].label}
                </span>
                <span className="text-[var(--warm-500)] text-[0.75rem]">
                  {reaction.chapterRef}
                </span>
              </div>
              <blockquote className="text-[var(--warm-700)] italic leading-7" style={{ fontSize: "0.95rem" }}>
                “{reaction.anchorQuote}”
              </blockquote>
            </div>
          ))}
        </div>

        <div className="relative z-10 max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <p className="text-[var(--amber-accent)] mb-4 tracking-widest uppercase" style={{ fontSize: "0.75rem", fontWeight: 500, letterSpacing: "0.15em" }}>
              {LANDING_HERO.eyebrow}
            </p>
            <h1 className="font-['Lora',Georgia,serif] text-[var(--warm-900)] mb-6" style={{ fontSize: "clamp(3.2rem, 7vw, 5.4rem)", fontWeight: 500, lineHeight: 1.08 }}>
              {LANDING_HERO.title}
              <br />
              <span className="italic text-[var(--amber-accent)]">{LANDING_HERO.emphasis}</span>
            </h1>
            <p className="text-[var(--warm-600)] max-w-3xl mx-auto mb-10" style={{ fontSize: "1.125rem", lineHeight: 1.8 }}>
              {LANDING_HERO.description}
            </p>
            <div className="flex items-center justify-center gap-4 flex-wrap">
              <Link
                to={LANDING_HERO.primaryCta.to}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg no-underline transition-colors bg-[var(--amber-accent)] text-white hover:bg-[var(--warm-700)]"
                style={{ fontSize: "0.9375rem", fontWeight: 500 }}
              >
                {LANDING_HERO.primaryCta.label}
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to={LANDING_HERO.secondaryCta.to}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg no-underline transition-colors border border-[var(--warm-300)] text-[var(--warm-700)] hover:bg-[var(--warm-200)]"
                style={{ fontSize: "0.9375rem", fontWeight: 500 }}
              >
                <Upload className="w-4 h-4" />
                {LANDING_HERO.secondaryCta.label}
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="px-6 py-18 bg-white/50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-[var(--amber-accent)] mb-2 tracking-widest uppercase" style={{ fontSize: "0.75rem", fontWeight: 500, letterSpacing: "0.15em" }}>
              {LANDING_REACTION_SECTION.eyebrow}
            </p>
            <h2 className="font-['Lora',Georgia,serif] text-[var(--warm-900)]" style={{ fontSize: "1.75rem", fontWeight: 500 }}>
              {LANDING_REACTION_SECTION.title}
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {LANDING_REACTION_CARDS.map((item, index) => {
              const Icon = landingIcons[item.key];
              const meta = reactionMeta[item.accentType];
              return (
                <motion.div
                  key={item.title}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.08 }}
                  className={`rounded-xl border border-[var(--warm-300)]/30 p-6 ${meta.surfaceClass}`}
                >
                  <div className="flex items-center gap-3 mb-3">
                    <Icon className={`w-5 h-5 ${meta.accentClass}`} />
                    <h3 className="font-['Lora',Georgia,serif] text-[var(--warm-900)]" style={{ fontSize: "1rem", fontWeight: 600 }}>
                      {item.title}
                    </h3>
                  </div>
                  <p className="text-[var(--warm-600)]" style={{ fontSize: "0.875rem", lineHeight: 1.7 }}>
                    {item.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="px-6 py-20">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-[var(--amber-accent)] mb-2 tracking-widest uppercase" style={{ fontSize: "0.75rem", fontWeight: 500, letterSpacing: "0.15em" }}>
              {LANDING_PREVIEW_SECTION.eyebrow}
            </p>
            <h2 className="font-['Lora',Georgia,serif] text-[var(--warm-900)] mb-3" style={{ fontSize: "1.75rem", fontWeight: 500 }}>
              {LANDING_PREVIEW_SECTION.title}
            </h2>
            <p className="text-[var(--warm-600)] max-w-2xl mx-auto mb-3" style={{ fontSize: "0.9375rem", lineHeight: 1.7 }}>
              {LANDING_PREVIEW_SECTION.description}
            </p>
            <p className="text-[var(--warm-600)]" style={{ fontSize: "0.9375rem" }}>
              {preview.sourceLabel} <span className="italic">{preview.sourceTitle}</span> by {preview.sourceAuthor}
            </p>
          </div>

          <div className="space-y-4">
            {preview.items.map((reaction, index) => (
              <motion.div
                key={reaction.reactionId}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 + index * 0.15 }}
                className="bg-white rounded-xl p-6 border border-[var(--warm-300)]/30 shadow-sm"
              >
                <div className="flex items-center gap-2 mb-3">
                  <span
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[var(--warm-900)] ${reactionMeta[reaction.type].surfaceClass}`}
                    style={{ fontSize: "0.75rem", fontWeight: 500 }}
                  >
                    {reactionMeta[reaction.type].label}
                  </span>
                  <span className="text-[var(--warm-500)]" style={{ fontSize: "0.75rem" }}>
                    {reaction.chapterRef} · {reaction.sectionRef}
                  </span>
                </div>
                <blockquote className="border-l-2 border-[var(--amber-accent)]/40 pl-4 mb-3 text-[var(--warm-600)] italic" style={{ fontSize: "0.875rem", lineHeight: 1.7 }}>
                  “{reaction.anchorQuote}”
                </blockquote>
                <p className="text-[var(--warm-800)]" style={{ fontSize: "0.9375rem", lineHeight: 1.8 }}>
                  {reaction.content}
                </p>
              </motion.div>
            ))}
          </div>

          <div className="text-center mt-10">
            <Link
              to={preview.ctaTo}
              className="inline-flex items-center gap-2 text-[var(--amber-accent)] no-underline hover:text-[var(--warm-700)] transition-colors"
              style={{ fontSize: "0.9375rem", fontWeight: 500 }}
            >
              {LANDING_PREVIEW_SECTION.ctaLabel}
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      <footer className="px-6 py-12 border-t border-[var(--warm-300)]/30">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-[var(--warm-500)]" style={{ fontSize: "0.8125rem" }}>
            {LANDING_FOOTER_COPY}
          </p>
        </div>
      </footer>
    </div>
  );
}
