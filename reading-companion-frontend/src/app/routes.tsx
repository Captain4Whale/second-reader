import { createBrowserRouter, Navigate, useParams } from "react-router";
import { RootLayout } from "./components/layout";
import { LandingPage } from "./components/landing-page";
import { BookshelfPage } from "./components/bookshelf-page";
import { AnalysisPage } from "./components/analysis-page";
import { BookOverviewPage } from "./components/book-overview-page";
import { ChapterReadPage } from "./components/chapter-read-page";
import { GlobalMarksPage } from "./components/global-marks-page";
import { UploadPage } from "./components/upload-page";
import { APP_ROUTE_TABLE } from "./route-config";
import {
  CANONICAL_ROUTE_PATTERNS,
  COMPAT_ROUTE_PATTERNS,
  UTILITY_ROUTE_PATTERNS,
  canonicalBookAnalysisPath,
  canonicalBookPath,
  canonicalChapterPath,
} from "./lib/contract";

function LegacyBookRedirect() {
  const { bookId = "" } = useParams();
  return <Navigate to={canonicalBookPath(bookId)} replace />;
}

function LegacyChapterRedirect() {
  const { bookId = "", chapterId = "" } = useParams();
  return <Navigate to={canonicalChapterPath(bookId, chapterId)} replace />;
}

function LegacyAnalysisRedirect() {
  const { bookId = "" } = useParams();
  return <Navigate to={canonicalBookAnalysisPath(bookId)} replace />;
}

function LegacyBooksRedirect() {
  return <Navigate to={CANONICAL_ROUTE_PATTERNS.books} replace />;
}

function LegacyMarksRedirect() {
  return <Navigate to={CANONICAL_ROUTE_PATTERNS.marks} replace />;
}

function LegacySampleRedirect() {
  return <Navigate to={CANONICAL_ROUTE_PATTERNS.books} replace />;
}

export const router = createBrowserRouter([
  {
    path: "/",
    Component: RootLayout,
    children: [
      { index: true, Component: LandingPage },
      { path: UTILITY_ROUTE_PATTERNS.upload.slice(1), Component: UploadPage },
      { path: UTILITY_ROUTE_PATTERNS.sample.slice(1), Component: LegacySampleRedirect },
      { path: CANONICAL_ROUTE_PATTERNS.books.slice(1), Component: BookshelfPage },
      { path: CANONICAL_ROUTE_PATTERNS.marks.slice(1), Component: GlobalMarksPage },
      { path: COMPAT_ROUTE_PATTERNS.bookshelf.slice(1), Component: LegacyBooksRedirect },
      { path: COMPAT_ROUTE_PATTERNS.marks.slice(1), Component: LegacyMarksRedirect },
      { path: COMPAT_ROUTE_PATTERNS.analysis.slice(1), Component: LegacyAnalysisRedirect },
      { path: COMPAT_ROUTE_PATTERNS.book.slice(1), Component: LegacyBookRedirect },
      { path: COMPAT_ROUTE_PATTERNS.chapter.slice(1), Component: LegacyChapterRedirect },
      { path: CANONICAL_ROUTE_PATTERNS.book.slice(1), Component: BookOverviewPage },
      { path: CANONICAL_ROUTE_PATTERNS.analysis.slice(1), Component: AnalysisPage },
      { path: CANONICAL_ROUTE_PATTERNS.chapter.slice(1), Component: ChapterReadPage },
    ],
  },
]);
