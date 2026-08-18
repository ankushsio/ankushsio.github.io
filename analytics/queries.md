# Reading the visit log

At this site's volume — tens of visits a week, not thousands — the Cloudflare
dashboard is the wrong instrument. Aggregate charts smooth away exactly the thing you
want, which is **individual arrivals you can read one at a time**. These queries are
built for n≈40, not n≈40,000.

Run any of them with:

```
./site/node_modules/.bin/wrangler d1 execute portfolio-visits --remote --command "<SQL>"
```

Add `--json` to pipe into something. Swap `--remote` for `--local` to query the
throwaway local copy instead of production.

---

## The question that matters: did the resume land?

Anyone you send the PDF to clicks through to the site and never touches the PDF
again — so `ref` is the whole funnel. `cv` means a resume you sent; `cv-<company>`
means a specific application; `cv-site` means they downloaded it *from* the site, so
it is not evidence your resume reached anyone.

```sql
SELECT day, ref, COUNT(DISTINCT visitor) AS people, COUNT(*) AS hits
FROM visit
WHERE ref IS NOT NULL AND is_bot = 0
GROUP BY day, ref
ORDER BY day DESC;
```

## Sessions, deepest first — did they actually read it?

Depth beats dwell time here. Someone who reached a case study is interested; someone
who bounced off `/` is not. This is also your best bot filter: **a human loads several
pages, a link scanner loads exactly one.**

```sql
SELECT visitor, day, COUNT(*) AS pages, MAX(org) AS org, MAX(country) AS country,
       MAX(ref) AS ref, GROUP_CONCAT(path, '  →  ') AS journey
FROM visit
WHERE kind = 'page' AND is_bot = 0
GROUP BY visitor, day
ORDER BY pages DESC, day DESC
LIMIT 40;
```

## Who, roughly

`org` is the ASN owner. A corporate network is a strong tell; a residential ISP is
probably you or a friend. Datacentre orgs on a single-page session are almost always
a scanner, whatever the user agent claims.

```sql
SELECT COALESCE(org,'?') AS org, country, COUNT(DISTINCT visitor) AS people,
       COUNT(*) AS hits, MAX(ts) AS last_seen
FROM visit
WHERE kind = 'page' AND is_bot = 0
GROUP BY org, country
ORDER BY hits DESC LIMIT 25;
```

## Where they came from

Empty `referer` plus a `ref` marker means a PDF click. Empty on both usually means
typed, bookmarked, or an app that strips the header.

```sql
SELECT COALESCE(NULLIF(referer,''),'(none)') AS came_from,
       COUNT(DISTINCT visitor) AS people, COUNT(*) AS hits
FROM visit WHERE kind='page' AND is_bot=0
GROUP BY came_from ORDER BY hits DESC;
```

## Raw feed — just read the last 30 things that happened

Honestly the most useful one. Read it like a log, not a metric.

```sql
SELECT ts, kind, path, COALESCE(ref,'-') AS ref, COALESCE(country,'?') AS cc,
       COALESCE(org,'?') AS org, is_bot
FROM visit ORDER BY id DESC LIMIT 30;
```

## Resume downloads specifically

```sql
SELECT ts, COALESCE(country,'?') AS cc, COALESCE(org,'?') AS org, referer
FROM visit WHERE kind='resume' AND is_bot=0 ORDER BY id DESC;
```

---

## Two things that will mislead you

**Corporate link scanners.** Outlook SafeLinks and Proofpoint fetch every URL in a
recruiter's inbox before a human sees it. They arrive with a browser user agent from a
datacentre ASN and fetch exactly one URL. Without filtering you would conclude your
resume is landing beautifully when a security appliance read it. `is_bot` catches the
honest ones; the one-page-session-from-a-datacentre pattern catches the rest.

**`visitor` is not a person.** It is `SHA-256(ip | user-agent | day)`, so it rotates at
midnight by construction and no IP is ever stored. Within a day it groups a session;
across days it cannot, by design. If cross-day return visits ever matter more than the
privacy property, swap the day for a fixed secret salt — but nothing here needs that.
