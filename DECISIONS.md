# Decisions taken while you were asleep

Everything here is reversible. Each entry says what I chose, why, and how to undo it.

---

## 1. Design direction: A ("Registration"), with B's timeline grafted in

**Chose** the editorial/typographic direction as the site's identity, and took the span
timeline from the warm-minimal direction for the Path page.

**Why.** Your stated bar was "must not look like AI slop". The sans-serif card grid that
direction B is built on is the single most common shape on the modern web, and it is the one
a reader is most likely to have seen before. The serif editorial treatment is rarer among
engineer portfolios and reads as considered rather than assembled. B's timeline was worth
keeping because it is information, not decoration — it shows overlap and duration honestly.

**To undo.** The whole design is CSS custom properties in `site/src/styles/global.css`.
Swapping to B's palette and font stack is a token change, not a rewrite.

Both samples are still live if you want to compare:
- A — https://claude.ai/code/artifact/abcb02da-73d9-45cb-ba75-0d1a82973e25
- B — https://claude.ai/code/artifact/35c15f7b-453e-49a2-8169-289a9cc59142

## 2. No Tailwind

Plain CSS with custom properties. The design is token-driven anyway, and a portfolio this
size gets nothing from a utility framework except a build step and a config file.

## 3. Astro, static output, no client-side JS

Ships zero JavaScript. Same static output works on GitHub Pages today and Cloudflare Workers
later, which is what makes the eventual cutover a DNS change rather than a rebuild.

## 4. Résumé built with Typst, deliberately in a different typeface from the site

The site is serif because it is for reading. The résumé is Calibri/Carlito because it is
optimised for density and machine parsing. Divergence is intentional, not an oversight.

## 5. Extraction scripts are NOT in the public repo

`extract_timesheets.py`, `extract_evals.py` and `classify_projects.py` encode client names in
their column mappings — that is unavoidable, since the raw spreadsheets label columns by
client. They are gitignored and stay on your machine. `privacy_gate.py` and
`sync-content.mjs` are safe and committed.

## 6. Commit authorship rewritten to a GitHub noreply address

Git was configured with your work email address, which is on a client's domain. On a public
repo that address is permanently visible in every commit — and it identifies the client. Rewrote both commits to
`33591091+ankushsio@users.noreply.github.com` and set it as the repo-local default.

This is worth flagging because the privacy gate cannot catch it: the gate greps file
contents, and this lives in git metadata.

## 7. `gh` was defaulting to your work account

Your work account was the active one; the first push was rejected with a 403. Switched to
`ankushsio` and set a repo-local credential helper (`!gh auth git-credential`) so this repo
always authenticates as your personal account regardless of the global default.

## 8. The `entertoescape` source link is not published

That repo is private, so a "Source" link would 404 for every visitor. The personal page shows
only the play link. Make the repo public and the link appears automatically — the template
already filters on `repo_is_private` in `content/career.json`.

## 9. Small factual corrections

- **Dropped C# from your skills.** I had inferred it from the Debian-packaging work on the
  access-control project; there is no evidence for it in the timesheets. Say the word and it
  goes back.
- **Added acronym forms** — "RBAC" alongside "role-based access control", "GCP" alongside
  "Google Cloud Platform", "SSE", "IaC". This was found by the ATS coverage check: a
  recruiter searching literally for "RBAC" would not have matched your résumé.
- **Added "HL7 FHIR"** rather than bare "HL7" — you have FHIR/HAPI experience, and FHIR is an
  HL7 standard, but that is not the same as HL7 v2 messaging. The precise form is defensible;
  bare "HL7" would have been a stretch.
- **Reassigned one timesheet entry** (2025-06-03) to the retinal-imaging project — it
  describes reviving your image-registration code, not work on the sibling system it was
  filed under. 8 hours; immaterial to totals, but it keeps that story accurate.

## 10. A minor sibling system folded into the Document AI case study

32 hours across four scattered days: codebase familiarisation, AWS metrics, and debugging. It
was not a project you owned — your own evaluation describes it as the system your RabbitMQ
broker connected the document pipeline to. A case study would have overstated it.

## 11. Two leaks happened, both caught

The first version of this very file named a client and your work email while explaining why
those must not be published. I chained the privacy gate through `| head` in my shell, which
swallowed its exit code, so the commit went through. **CI ran the gate and failed the
deploy** — so nothing broken ever reached the live site. The commit was then rewritten out of
history with a force push.

**The second** was a phone number: approving "phone on the PDF, not the website" was
implemented by putting it in `content/career.json`, which is public — and the PDF is served
*from* the website anyway, so the distinction was meaningless as built. Phone now lives in the
gitignored `resume/private.json`, renders only via `render_resume.py --phone`, and the build
published to the site omits it. The gate now detects phone numbers too.

Three things worth keeping: the gate belongs in CI because a local check can be bypassed by
accident (a shell pipe swallowed its exit code the first time); a name-based check cannot
catch a number, so PII patterns had to be added explicitly; and a force push leaves the blob
unreachable from any ref but not erased — GitHub Support can purge the orphan if it ever
matters. Ankush decided it did not.

## 12. Hosting moved to Cloudflare Workers, in one step instead of two (2026-08-17)

The original plan was GitHub Pages now, Cloudflare later. That was chosen for a real reason —
Pages is fully automatable from the CLI with no secrets, whereas Workers Builds needs one
manual dashboard connection. Doing it in two phases meant paying the DNS-and-certificate cost
twice, so it collapsed into one move.

**Analytics decided it.** GitHub Pages provides none at all — no logs, no dashboard, no API —
so the only option there was a client-side beacon that ad blockers strip and crawlers never
trigger. On Workers the request data is server-side and unblockable.

The migration also deleted a constraint rather than satisfying it. Under Pages, the `me` CNAME
had to stay **grey-clouded**, because GitHub needed Let's Encrypt to reach *its* servers to
answer an ACME challenge; proxying broke issuance. A Cloudflare custom domain has no third
party in that loop, so the whole grey-cloud rule simply stopped existing.

What it looks like now: `wrangler.jsonc` at the repo root, assets from `site/dist`,
`run_worker_first` narrowed to `/ankush-jain-resume.pdf` so page views cost **zero** Worker
invocations. `src/worker/index.js` runs on that one path to log downloads with country and
requesting network. Non-production branches get a preview URL each via `wrangler versions
upload`, which Pages could never do — it has one environment per repo.

`.github/workflows/deploy.yml` was kept, not deleted: it is still the CI gate (privacy gate →
build → coverage) and it keeps `ankushsio.github.io` fresh as a fallback. `site/public/CNAME`
was deleted, because leaving it would have GitHub Pages contend for a domain Cloudflare now
owns.

---

# Open items — these need you

1. ~~Your current résumé~~ — **done.** Four drafts supplied; ByteLearn, Deloitte USI, the
   three internships, achievements and education are all in and on the site.
2. ~~Contact details~~ — **done.** Email, LinkedIn, Bengaluru. Phone lives in the
   gitignored `resume/private.json` and renders only with `render_resume.py --phone`.
3. ~~The Cloudflare DNS record~~ — **done, and not the way this file used to describe it.**
   The site no longer runs on GitHub Pages, so the grey-cloud CNAME and the *Enforce HTTPS*
   step that used to be listed here do not apply and would undo the current setup if followed.
   `me.entertoescape.com` is a **Cloudflare Workers custom domain**, attached in the Worker's
   dashboard — Cloudflare creates the DNS record itself, proxied, and issues the certificate.
   There was never a record to add by hand. See §12.
4. ~~`portfolio.entertoescape.com` → `me.entertoescape.com/work`~~ — **dropped.** The second
   hostname was never clearly worth its own redirect rule; one canonical URL is simpler to put
   on a résumé. Revisit only if something already links to the old subdomain.
5. ~~GA4 measurement ID~~ — **closed, not skipped.** Moving to Workers made it redundant:
   traffic data now comes from Cloudflare zone analytics and the `resume_download` lines in
   Workers Logs, both server-side. GA4 would be a strictly worse duplicate — client-side, so
   ad blockers strip it, and blind to crawlers. Nothing to add.
6. ~~Decide on the `entertoescape` repo~~ — **decided: it stays private.** The `Source` link
   stays in `career.json` because it is genuinely the source; `repo_is_private: true` makes
   `personal.astro` suppress it, so nothing on the live site 404s. Flip that one flag if the
   repo is ever opened and the link renders itself.

   Still worth a look at some point: `why_it_matters` on that entry says *"the one project I
   can hand someone the source for"*, which reads oddly next to a suppressed link. Copy, not
   a defect.
