// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

/**
 * The repo is named `ankushsio.github.io`, so the GitHub Pages mirror serves from the
 * domain root -- exactly like the custom domain does. That is why there is no `base`
 * here, and why moving from GitHub Pages to Cloudflare Workers later is a DNS change
 * rather than a rebuild.
 */
export default defineConfig({
  site: "https://me.entertoescape.com",
  integrations: [sitemap()],
  trailingSlash: "ignore",
  build: {
    format: "directory",
  },
  compressHTML: true,
});
