"""
Fail the build if a quantified achievement never reaches the LinkedIn copy.

    python scripts/check_metric_coverage.py

Why this exists
---------------
The $200+/month cloud saving sat in career.json and flowed into the resume for weeks
while being absent from LinkedIn entirely. Nothing caught it, because linkedin_about()
and linkedin_experience() in build_docs.py are hand-written prose that ignores
career.json -- two independently curated sets of bullets with nothing enforcing that
they agree. A number strong enough to put on a one-page resume is strong enough for the
surface with three times the room, so silently dropping one is always a mistake.

`check_site_coverage.py` guards the same class of bug on the site. This is its LinkedIn
counterpart.

How a metric is matched
-----------------------
Not by scanning for digits. The LinkedIn copy legitimately reframes the same win --
career.json states the AR latency fix as "22s to 2s" while LinkedIn says "over 80% of
its time removed", and none of the digits survive. Matching on numbers produced false
failures on exactly the highlights that were fine.

So each `metric: true` highlight declares its own anchor:

    "linkedin_figure": "over 80%"      must appear verbatim in some linkedin/*.txt
    "linkedin_omit":   "<reason>"      deliberately not on LinkedIn, and says why

A metric with neither field fails. That is the point: leaving a number off LinkedIn
becomes a decision someone wrote down, rather than an oversight nobody noticed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAREER = ROOT / "content" / "career.json"
LINKEDIN = ROOT / "linkedin"


def metric_highlights(node, found=None):
    """Every highlight marked metric: true, wherever it sits in the tree."""
    if found is None:
        found = []
    if isinstance(node, dict):
        if node.get("metric") and isinstance(node.get("text"), str):
            found.append(node)
        for value in node.values():
            metric_highlights(value, found)
    elif isinstance(node, list):
        for value in node:
            metric_highlights(value, found)
    return found


def main() -> int:
    career = json.loads(CAREER.read_text(encoding="utf-8"))

    sources = sorted(LINKEDIN.glob("*.txt")) + sorted((LINKEDIN / "projects").glob("*.txt"))
    if not sources:
        print("ERROR: no linkedin/*.txt files -- run scripts/build_docs.py first",
              file=sys.stderr)
        return 1
    copy = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8") for p in sources}

    metrics = metric_highlights(career)
    if not metrics:
        print("ERROR: no metric highlights found in career.json", file=sys.stderr)
        return 1

    problems: list[str] = []
    omitted: list[str] = []
    matched = 0

    for h in metrics:
        hid = h.get("id", "<no id>")
        figure = h.get("linkedin_figure")
        omit = h.get("linkedin_omit")

        if omit:
            omitted.append(f"{hid} -- {omit}")
            continue

        if not figure:
            problems.append(
                f"{hid}: metric highlight has neither `linkedin_figure` nor "
                f"`linkedin_omit`.\n"
                f"    {h['text'][:100]}\n"
                f"    Add the exact substring that carries this number on LinkedIn, or "
                f"state why it is left off."
            )
            continue

        where = [name for name, text in copy.items() if figure in text]
        if where:
            matched += 1
        else:
            problems.append(
                f"{hid}: `linkedin_figure` {figure!r} appears in no LinkedIn file.\n"
                f"    {h['text'][:100]}\n"
                f"    Either add it to the copy in scripts/build_docs.py and "
                f"regenerate, or set `linkedin_omit` with a reason."
            )

    if problems:
        print(f"metric coverage: FAILED -- {len(problems)} of {len(metrics)} "
              f"quantified achievements are unaccounted for\n", file=sys.stderr)
        for p in problems:
            print(f"  - {p}\n", file=sys.stderr)
        return 1

    print(f"metric coverage: OK - {matched} of {len(metrics)} quantified achievements "
          f"present in the LinkedIn copy")
    for o in omitted:
        print(f"  (deliberately omitted: {o})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
