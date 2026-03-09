import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendRoot = path.resolve(__dirname, "..");
const snapshotPath = path.resolve(frontendRoot, "../contract/openapi.public.snapshot.json");
const generatedPath = path.resolve(frontendRoot, "src/app/lib/generated/api-schema.d.ts");

function normalize(text: string): string {
  return text.replace(/\r\n/g, "\n");
}

function main(): void {
  assert.ok(fs.existsSync(snapshotPath), `Missing OpenAPI snapshot at ${snapshotPath}.`);
  assert.ok(fs.existsSync(generatedPath), `Missing generated API types at ${generatedPath}. Run 'npm run generate-api-types'.`);

  const result = spawnSync(
    "npx",
    ["openapi-typescript", "../contract/openapi.public.snapshot.json"],
    {
      cwd: frontendRoot,
      encoding: "utf-8",
    },
  );

  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || "openapi-typescript failed.");
  }

  const expected = normalize(result.stdout);
  const current = normalize(fs.readFileSync(generatedPath, "utf-8"));
  assert.equal(
    current,
    expected,
    "Generated API types drifted from contract/openapi.public.snapshot.json. Run 'npm run generate-api-types'.",
  );

  process.stdout.write("Generated API types match the OpenAPI snapshot.\n");
}

main();
