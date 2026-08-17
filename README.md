# me.entertoescape.com

Personal portfolio and résumé source for Ankush Jain. Built with Astro, deployed to
GitHub Pages by GitHub Actions on every push to `main`.

- **Live:** https://me.entertoescape.com
- **Mirror:** https://ankushsio.github.io

## How this is put together

Everything on the site and in every résumé is generated from one file:
[`content/career.json`](content/career.json). Project pages, the career timeline, the web
résumé and the PDF all read from it, so they cannot drift apart. Each claim in it carries a
`source` field pointing back at the record it came from.

```
content/career.json      single source of truth (public, anonymised)
site/                    Astro app
  src/components/diagrams/   hand-authored inline-SVG architecture figures
  src/pages/work/[slug]      one case study per project
resume/
  template.typ           one-page ATS-first Typst template
  variants/base.json     which highlights appear, and their JD-tuned wording
  private.json           GITIGNORED - phone, rendered only with --phone
linkedin/                copy-paste blocks, within LinkedIn's character limits
scripts/
  render_resume.py       variant -> PDF, asserts the page count
  ats_check.py           parse-back + JD keyword coverage on the rendered PDF
  build_docs.py          master.md + LinkedIn copy from career.json
  privacy_gate.py        fails the build on client names, codenames or phone numbers
  check_site_coverage.py fails the build if career.json data renders on no page
  sync-content.mjs       copies career.json into the Astro app before dev/build
design/                  the two design directions the site was chosen from
```

## Confidentiality

The site describes client work without naming clients. **Apra Labs — the employer — is the
only company named.** Projects are described by engineering, technology and generic domain.

`scripts/privacy_gate.py` enforces this. It greps every tracked file for client names,
internal codenames and colleague names, and exits non-zero on a hit. It runs in CI on every
push, and should be run locally before pushing:

```bash
python scripts/privacy_gate.py        # client names, codenames, colleague names, phone numbers
python scripts/check_site_coverage.py # every career.json entry reaches a page
```

Both run in CI on every push. The coverage check exists because data was twice added to
`career.json`, rendered in the PDF, and silently missing from the site.

The source data this was built from — timesheets, self-evaluations, and the scripts that
parse them — is gitignored and never leaves the machine. Those extraction scripts
(`extract_timesheets.py`, `extract_evals.py`, `classify_projects.py`) encode client names in
their column mappings, which is exactly why they are not published.

## Local development

```bash
cd site
npm install
npm run dev      # http://localhost:4321
npm run build    # -> site/dist
npm run preview
```

`npm run dev` and `npm run build` both run `sync-content.mjs` first, which copies
`content/career.json` into `site/src/data/`. Never edit that copy — it is overwritten.

## Deployment

Push to `main`. The workflow in `.github/workflows/deploy.yml` runs the privacy gate,
builds, and deploys to GitHub Pages using OIDC — there are no secrets to manage.

The custom domain requires one manual DNS record in Cloudflare:

| Type | Name | Target | Proxy |
|---|---|---|---|
| CNAME | `me` | `ankushsio.github.io` | **DNS only (grey cloud)** |

Proxying breaks GitHub's certificate issuance. It goes back to proxied only if the site
later moves to Cloudflare Workers, at which point the build output is unchanged and the
cutover is a DNS change.
