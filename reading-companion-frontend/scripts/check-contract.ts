import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { LANDING_PREVIEW_CONFIG, LANDING_REACTION_CARDS, LANDING_SAMPLE_TEASERS } from "../src/app/content/landing-content";
import {
  CANONICAL_ROUTE_PATTERNS,
  COMPAT_ROUTE_LIST,
  LANDING_STRATEGY,
  PUBLIC_CONTRACT_SPEC,
} from "../src/app/lib/contract";
import { APP_ROUTE_TABLE } from "../src/app/route-config";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendRoot = path.resolve(__dirname, "..");
const srcRoot = path.join(frontendRoot, "src");

async function readText(relativePath: string): Promise<string> {
  return fs.readFile(path.join(frontendRoot, relativePath), "utf-8");
}

async function collectSourceFiles(dir: string): Promise<string[]> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    if (entry.name.startsWith(".")) {
      continue;
    }
    const nextPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await collectSourceFiles(nextPath)));
      continue;
    }
    if (/\.(ts|tsx)$/.test(entry.name)) {
      files.push(nextPath);
    }
  }
  return files;
}

async function main(): Promise<void> {
  assert.equal(
    LANDING_REACTION_CARDS.length,
    LANDING_STRATEGY.display_card_count,
    "Landing display card count drifted from the contract.",
  );
  assert.ok(LANDING_SAMPLE_TEASERS.length > 0, "Landing sample teasers must come from static content.");
  assert.equal(LANDING_PREVIEW_CONFIG.mode, "api", "Landing preview must default to API-backed content.");
  assert.deepEqual(APP_ROUTE_TABLE.canonical, Object.values(CANONICAL_ROUTE_PATTERNS));
  assert.deepEqual(APP_ROUTE_TABLE.compatRoutes, [...COMPAT_ROUTE_LIST]);
  assert.deepEqual(
    APP_ROUTE_TABLE.compatRedirects.map((item) => item.from),
    [...COMPAT_ROUTE_LIST],
    "Compat routes must remain redirect-only entries.",
  );
  assert.deepEqual(APP_ROUTE_TABLE.utility, ["/upload"]);
  assert.deepEqual(PUBLIC_CONTRACT_SPEC.landing_strategy, LANDING_STRATEGY);

  const landingPageSource = await readText("src/app/components/landing-page.tsx");
  assert.match(landingPageSource, /from "\.\.\/content\/landing-content"/);
  assert.doesNotMatch(landingPageSource, /const reactionCards\s*=/);
  assert.doesNotMatch(landingPageSource, /const teaserReactions\s*=/);

  const sourceFiles = await collectSourceFiles(srcRoot);
  const bannedPatterns = ["/api/landing", "/api/sample", "fetchLanding", "fetchSample", '"/sample"', "'/sample'"];
  const bannedVisibleCopy = [
    "DeepRead",
    "初版原型",
    "Current Product Strategy",
    "Contract Notes",
    "The canonical web routes",
    "frontend-owned",
    "Hardcoded on purpose",
    "The backend accepts EPUB uploads",
    "WebSocket endpoint",
  ];
  for (const filePath of sourceFiles) {
    const contents = await fs.readFile(filePath, "utf-8");
    for (const pattern of bannedPatterns) {
      assert.ok(
        !contents.includes(pattern),
        `Frontend source still references banned landing/sample API token '${pattern}' in ${path.relative(frontendRoot, filePath)}.`,
      );
    }
    for (const text of bannedVisibleCopy) {
      assert.ok(
        !contents.includes(text),
        `Frontend source still exposes banned copy '${text}' in ${path.relative(frontendRoot, filePath)}.`,
      );
    }
  }

  const indexHtml = await readText("index.html");
  for (const text of bannedVisibleCopy) {
    assert.ok(!indexHtml.includes(text), `Frontend static file index.html still exposes banned copy '${text}'.`);
  }

  process.stdout.write("Frontend contract check passed.\n");
}

await main();
