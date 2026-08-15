# Résumé

Two artifacts, one source:

- **`master.md`** — the complete record, no page limit. Generated from
  `content/career.json`. Never sent to an employer; it is what tailored versions are cut
  from.
- **`build/<variant>/resume.pdf`** — a one-page PDF for a specific application.

Both regenerate from `content/career.json`, so editing that file updates everything.

## Rendering

```bash
python scripts/build_docs.py          # master.md + LinkedIn copy
python scripts/render_resume.py       # the base one-pager
python scripts/ats_check.py           # format lint on the rendered PDF
```

`render_resume.py` asserts the page count and exits non-zero if the résumé spills past one
page. The shipped copy lives at `site/public/ankush-jain-resume.pdf` and is what the site
links to — re-copy it after a change.

## Tailoring for a job description

```bash
cp resume/variants/base.json resume/variants/acme.json
# edit summary, choose bullets, rewrite wording to match the JD
python scripts/render_resume.py acme
python scripts/ats_check.py acme path/to/jd.txt
cp resume/build/acme/resume.pdf ~/applications/acme.pdf
```

**This is not pure selection.** Lifting bullets verbatim from `career.json` would both
overflow one page and read generically. `career.json` is the *evidence base*; a variant may
rewrite any bullet's wording to mirror the job description's language.

Two rules make that safe, and the renderer enforces the first one:

1. **Every bullet must reference a highlight `id` that exists in `career.json`.** An unknown
   id is a hard error. Wording is tailored; the underlying claim is not. This is what stops
   a tailored résumé from drifting into invention.
2. **One page is a hard constraint**, checked mechanically rather than eyeballed.

### When it does not fit

In this order:

1. Cut the weakest bullet.
2. Tighten wording — most bullets have 10–20% of slack in them.
3. Only then adjust leading or margins, within limits.

**Do not** shrink type below 10 pt or margins below 0.5 in to force a fit. If it still does
not fit, the content is too long and should be cut, not squeezed.

## On ATS

There is no universal ATS score. Greenhouse, Lever, Workday and Taleo mostly parse and
store résumés; recruiters then search by keyword. The percentage scores sold by résumé
checkers are each a proprietary invention and do not transfer between systems, so
`ats_check.py` reports none.

It checks the two things that genuinely cause rejection:

- **Parse.** It extracts text back out of the *rendered PDF*. If extraction is empty,
  garbled, or out of reading order, that is the failure a real ATS hits. The template avoids
  what actually breaks parsers: multiple columns, tables, text boxes, images standing in for
  text, and contact details in a page header or footer.
- **Coverage.** Given a job description, it names which of the JD's terms are absent, so
  gaps get closed with true statements.

Coverage checking has already earned its keep once: the résumé said "role-based access
control" but not "RBAC", so a recruiter's literal keyword search would have missed it. Both
forms are now present. Same for "GCP" alongside "Google Cloud Platform".

**Only add a missing keyword when it is true and evidenced in `career.json`.** Keyword
stuffing fails the moment a human reads the page, and a human always does eventually.
