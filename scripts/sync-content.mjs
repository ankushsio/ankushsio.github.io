/**
 * Copy the canonical career record into the Astro app.
 *
 * `content/career.json` at the repo root is the single source of truth for the site,
 * the resumes and the LinkedIn copy. Astro/Vite will not import from outside its own
 * root, so this runs before dev and build to place a copy where the app can import it.
 * Never edit site/src/data/career.json by hand -- it is overwritten on every build.
 */

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..");

const source = join(root, "content", "career.json");
const destDir = join(root, "site", "src", "data");
const dest = join(destDir, "career.json");

// Fail loudly on malformed JSON rather than shipping a broken build.
JSON.parse(readFileSync(source, "utf8"));

mkdirSync(destDir, { recursive: true });
copyFileSync(source, dest);

console.log(`sync-content: content/career.json -> site/src/data/career.json`);
