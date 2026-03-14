import { CANONICAL_ROUTE_PATTERNS, COMPAT_ROUTE_LIST, COMPAT_ROUTE_PATTERNS, UTILITY_ROUTE_PATTERNS } from "./lib/contract";

export const APP_ROUTE_TABLE = {
  canonical: [
    CANONICAL_ROUTE_PATTERNS.landing,
    CANONICAL_ROUTE_PATTERNS.books,
    CANONICAL_ROUTE_PATTERNS.book,
    CANONICAL_ROUTE_PATTERNS.chapter,
    CANONICAL_ROUTE_PATTERNS.marks,
  ],
  compatRedirects: [
    { from: COMPAT_ROUTE_PATTERNS.bookshelf, to: CANONICAL_ROUTE_PATTERNS.books },
    { from: COMPAT_ROUTE_PATTERNS.book, to: CANONICAL_ROUTE_PATTERNS.book },
    { from: COMPAT_ROUTE_PATTERNS.chapter, to: CANONICAL_ROUTE_PATTERNS.chapter },
    { from: COMPAT_ROUTE_PATTERNS.bookAnalysis, to: CANONICAL_ROUTE_PATTERNS.book },
    { from: COMPAT_ROUTE_PATTERNS.analysis, to: CANONICAL_ROUTE_PATTERNS.book },
    { from: COMPAT_ROUTE_PATTERNS.marks, to: CANONICAL_ROUTE_PATTERNS.marks },
  ],
  compatRoutes: [...COMPAT_ROUTE_LIST],
  utility: [UTILITY_ROUTE_PATTERNS.upload],
} as const;
