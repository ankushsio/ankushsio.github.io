-- Portfolio visit log.
--
-- Lives in D1 rather than Workers Logs on purpose: Workers Logs retain 3 days on the
-- free plan and 7 on paid, which is useless for a job search that runs months -- an
-- application sent on the 1st would be unreadable by the 8th. D1 has no retention
-- window and the volume here (tens of rows a week) is nowhere near any free limit.

CREATE TABLE IF NOT EXISTS visit (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  ts       TEXT    NOT NULL,          -- ISO-8601 UTC
  day      TEXT    NOT NULL,          -- YYYY-MM-DD, for cheap grouping
  visitor  TEXT    NOT NULL,          -- see note below: NOT a stable identity
  kind     TEXT    NOT NULL,          -- page | resume | meta
  host     TEXT    NOT NULL,          -- separates prod from *.workers.dev previews
  path     TEXT    NOT NULL,
  ref      TEXT,                      -- the ?r= marker, e.g. "cv" -- attribution
  referer  TEXT,
  country  TEXT,
  city     TEXT,
  asn      INTEGER,
  org      TEXT,                      -- ASN org: the recruiter-vs-ISP tell
  ua       TEXT,
  is_bot   INTEGER NOT NULL DEFAULT 0 -- coarse UA match; see also the org column
);

-- `visitor` is SHA-256(ip | user-agent | day) truncated to 16 hex chars. The day is
-- inside the hash, so the value rotates every midnight by construction. That buys
-- session grouping WITHIN a day -- "this person landed on /, then /work/, then a case
-- study" -- and deliberately gives up cross-day identity. No IP is ever stored.
-- Switch to a fixed secret salt if cross-day return visits ever matter more.

CREATE INDEX IF NOT EXISTS visit_ts_idx      ON visit(ts);
CREATE INDEX IF NOT EXISTS visit_day_idx     ON visit(day);
CREATE INDEX IF NOT EXISTS visit_visitor_idx ON visit(visitor);
CREATE INDEX IF NOT EXISTS visit_ref_idx     ON visit(ref);
