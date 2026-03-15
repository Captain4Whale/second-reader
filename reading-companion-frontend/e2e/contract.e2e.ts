import path from "node:path";
import { fileURLToPath } from "node:url";
import { expect, test, type Page } from "@playwright/test";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const uploadFixture = path.resolve(__dirname, "../../reading-companion-backend/tests/fixtures/e2e_runtime/sample-upload.epub");

function assertNoLegacyPath(pathname: string): void {
  expect(pathname.startsWith("/bookshelf")).toBeFalsy();
  expect(pathname.startsWith("/book/")).toBeFalsy();
  expect(pathname.startsWith("/analysis/")).toBeFalsy();
  expect(pathname.startsWith("/sample")).toBeFalsy();
}

async function expectNoLegacyMetrics(page: Page): Promise<void> {
  await expect(page.getByText(/high-signal/i)).toHaveCount(0);
  await expect(page.getByText("Reaction density")).toHaveCount(0);
  await expect(page.getByText("Top reaction type")).toHaveCount(0);
}

test("landing upload flows into canonical overview and chapter reading", async ({ page }) => {
  const requestedPaths: string[] = [];
  page.on("request", (request) => {
    try {
      requestedPaths.push(new URL(request.url()).pathname);
    } catch {
      // ignore non-standard URLs
    }
  });

  await page.goto("/");
  await expect(page).toHaveURL(/\/$/);
  assertNoLegacyPath(new URL(page.url()).pathname);

  await page.getByTestId("landing-upload-cta").click();
  await expect(page.getByTestId("landing-upload-dialog")).toBeVisible();
  await page.getByTestId("landing-upload-input").setInputFiles(uploadFixture);
  await expect(page).toHaveURL(/\/books\/\d+$/);
  assertNoLegacyPath(new URL(page.url()).pathname);
  await expect(page.getByRole("heading", { name: "Fixture E2E Book" })).toBeVisible();
  await expectNoLegacyMetrics(page);

  const completedCard = page.getByRole("link", { name: /Open (chapter|completed chapter)/i }).first();
  await expect(completedCard).toBeVisible({ timeout: 15_000 });
  await expect(completedCard).not.toContainText(/high-signal/i);
  await completedCard.click();
  await expect(page).toHaveURL(/\/books\/\d+\/chapters\/1$/);
  assertNoLegacyPath(new URL(page.url()).pathname);
  await expect(page.getByTestId("source-reader-pane")).toBeVisible();
  await expect(page.getByTestId("chapter-topbar")).toBeVisible();
  await expect(page.getByTestId("chapter-topbar")).toContainText("1 reactions");
  await expectNoLegacyMetrics(page);
  const chapterUrl = page.url();

  const reactionCard = page.locator('[data-testid^="reaction-card-"]').first();
  await expect(reactionCard).toBeVisible();
  const reactionTestId = await reactionCard.getAttribute("data-testid");
  const reactionId = reactionTestId?.replace("reaction-card-", "");
  expect(reactionId).toBeTruthy();
  await reactionCard.click();
  await expect(page).toHaveURL(new RegExp(`/books/\\d+/chapters/1\\?reaction=${reactionId}`));

  const firstMarkButton = page.locator('[data-testid^="mark-resonance-"]').first();
  await expect(firstMarkButton).toBeVisible();
  const markResponsePromise = page.waitForResponse((response) => {
    try {
      const pathname = new URL(response.url()).pathname;
      return ["PUT", "DELETE"].includes(response.request().method()) && /^\/api\/marks\/\d+$/.test(pathname);
    } catch {
      return false;
    }
  });
  await firstMarkButton.click();
  const markResponse = await markResponsePromise;
  expect(markResponse.ok()).toBeTruthy();
  await expectNoLegacyMetrics(page);

  await page.goto("/books");
  await expect(page).toHaveURL(/\/books$/);
  await expect(page.getByTestId("global-nav-books")).toHaveAttribute("aria-current", "page");
  const bookCard = page.locator('[data-testid^="book-card-"]').first();
  const bookHref = await bookCard.getAttribute("href");
  expect(bookHref).toMatch(/^\/books\/\d+$/);
  await bookCard.click();
  await expect(page).toHaveURL(/\/books\/\d+$/);
  await expect(page.getByTestId("book-overview-source-download")).toBeVisible();
  await expectNoLegacyMetrics(page);

  await page.goto(chapterUrl);
  await page.getByTestId("brand-link").click();
  await expect(page).toHaveURL(/\/$/);

  expect(requestedPaths).not.toContain("/api/landing");
  expect(requestedPaths).not.toContain("/api/sample");
});

test("bookshelf upload supports defer-start and compat redirects", async ({ page }) => {
  await page.goto("/upload");
  await expect(page).toHaveURL(/\/books(?:\?.*)?$/);
  await expect(page.getByTestId("bookshelf-upload-dialog")).toContainText("添加一本新书");

  await page.getByTestId("bookshelf-upload-input").setInputFiles(uploadFixture);

  await expect(page.getByRole("alertdialog")).toContainText("已添加到书架", { timeout: 15_000 });
  await page.getByRole("button", { name: "只进入书架" }).click();
  await expect(page).toHaveURL(/\/books$/);
  await expect(page.getByRole("alertdialog")).toBeHidden();

  const bookCard = page.locator('[data-testid^="book-card-"]').first();
  await expect(bookCard).toContainText("未开始");
  await bookCard.click();
  await expect(page).toHaveURL(/\/books\/\d+$/);
  assertNoLegacyPath(new URL(page.url()).pathname);
  await expect(page.getByRole("button", { name: "开始深读" })).toBeVisible();
  const bookUrl = page.url();

  await page.goto(`${bookUrl}/analysis`);
  await expect(page).toHaveURL(bookUrl);

  await page.getByRole("button", { name: "开始深读" }).click();
  await expect(page.getByText("深读进行中")).toBeVisible();
  await expect(page.getByRole("link", { name: /Chapter 1.*Open chapter/i }).first()).toBeVisible({ timeout: 15_000 });
  await expectNoLegacyMetrics(page);
});
