export const BRAND_CONFIG = {
  productName: "书虫",
  navigation: {
    booksLabel: "Bookshelf",
    marksLabel: "My Marks",
  },
  footer: {
    tagline: "An AI reading companion for those who read to think.",
    signature: "书虫 · An AI reading companion for those who read to think.",
  },
  pageTitles: {
    books: "书架",
    marks: "我的标记",
    upload: "上传",
    analysis: "分析中",
    book: "书籍详情",
    chapter: "章节深读",
  },
} as const;

export function getDocumentTitle(pathname: string): string {
  const normalized = pathname || "/";

  if (normalized === "/") {
    return BRAND_CONFIG.productName;
  }
  if (normalized === "/books") {
    return `${BRAND_CONFIG.productName} · ${BRAND_CONFIG.pageTitles.books}`;
  }
  if (normalized === "/marks") {
    return `${BRAND_CONFIG.productName} · ${BRAND_CONFIG.pageTitles.marks}`;
  }
  if (normalized === "/upload") {
    return `${BRAND_CONFIG.productName} · ${BRAND_CONFIG.pageTitles.upload}`;
  }
  if (/^\/books\/[^/]+\/analysis$/.test(normalized)) {
    return `${BRAND_CONFIG.productName} · ${BRAND_CONFIG.pageTitles.analysis}`;
  }
  if (/^\/books\/[^/]+\/chapters\/[^/]+$/.test(normalized)) {
    return `${BRAND_CONFIG.productName} · ${BRAND_CONFIG.pageTitles.chapter}`;
  }
  if (/^\/books\/[^/]+$/.test(normalized)) {
    return `${BRAND_CONFIG.productName} · ${BRAND_CONFIG.pageTitles.book}`;
  }
  return BRAND_CONFIG.productName;
}
