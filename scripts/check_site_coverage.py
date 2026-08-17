"""
Assert that everything in career.json actually reaches the built site.

    python scripts/check_site_coverage.py

Why this exists: twice, data was added to career.json and rendered in the PDF but not on
the site. The second time the cause was a page that only had a `{!hasPrior && ...}`
placeholder branch and no branch that rendered the data -- so populating the field made
the section disappear instead of appear. Nothing failed; the content was simply absent.

This check closes that gap. It reads the built HTML in site/dist and fails if any company,
role, project, internship, achievement or education entry is missing from it.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAREER = ROOT / "content" / "career.json"
DIST = ROOT / "site" / "dist"


def normalise(text: str) -> str:
    """Strip tags, unescape entities, collapse whitespace and normalise dashes."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = (text.replace("—", "-").replace("–", "-")
                .replace("’", "'").replace("‘", "'")
                .replace("“", '"').replace("”", '"'))
    return re.sub(r"\s+", " ", text)


def required(career: dict) -> list[tuple[str, str]]:
    """(label, needle) pairs that must appear in the built site."""
    items: list[tuple[str, str]] = []
    person = career["person"]

    items.append(("person name", person["name"]))
    items.append(("email", person["email"]))
    items.append(("location", person["location"]))
    items.append(("summary", person["summary"][:60]))

    # Positioning copy is display text unless the key starts with "_", which marks it as
    # internal guidance (e.g. _domain_note, which deliberately never ships).
    for key, value in career.get("positioning", {}).items():
        if key.startswith("_") or not isinstance(value, str) or len(value) < 40:
            continue
        items.append((f"positioning.{key}", value[:60]))
    for theme in career.get("positioning", {}).get("themes", []):
        items.append(("theme", theme[:60]))

    for company in career["companies"]:
        items.append(("company", company["name"]))
        for role in company.get("roles", []):
            items.append(("role", role["title"]))
        for project in company["projects"]:
            items.append(("project", project["title"]))
            # every highlight, not just the featured ones
            for h in project["highlights"]:
                items.append((f"highlight {h['id']}", h["text"][:60]))
        for h in company.get("cross_project_highlights", []):
            items.append((f"cross highlight {h['id']}", h["text"][:60]))

    prior = career.get("prior_experience", {})
    for job in prior.get("full_time", []):
        items.append(("prior company", job["company"]))
        items.append(("prior role", job["role"]))
        for h in job.get("highlights", []):
            items.append((f"prior highlight {h['id']}", h["text"][:60]))
    for job in prior.get("internships", []):
        items.append(("internship", job["company"]))
        items.append(("internship role", job["role"]))
        if job.get("summary"):
            items.append((f"internship summary {job['company']}", job["summary"]))
        for h in job.get("highlights", []):
            items.append((f"internship highlight {h['id']}", h["text"][:60]))

    for a in career.get("achievements", []):
        items.append(("achievement", a["text"][:60]))

    for e in career.get("education", []):
        items.append(("education", e["institution"]))
        items.append(("degree", e["degree"]))

    for p in career.get("personal_projects", []):
        items.append(("personal project", p["title"]))

    return items


def main() -> int:
    if not DIST.is_dir():
        sys.exit(f"ERROR: {DIST} not found — run `npm run build` in site/ first")

    career = json.loads(CAREER.read_text(encoding="utf-8"))
    pages = list(DIST.rglob("*.html"))
    if not pages:
        sys.exit(f"ERROR: no HTML found under {DIST}")

    haystack = normalise(
        "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in pages))

    missing = [
        (label, needle) for label, needle in required(career)
        if normalise(needle) not in haystack
    ]

    if missing:
        print(f"SITE COVERAGE FAILED — {len(missing)} item(s) in career.json never "
              f"reach the built site:\n")
        for label, needle in missing:
            print(f"  [{label}] {needle}")
        print("\nAdd them to a page, or remove them from career.json. Data that exists "
              "but renders nowhere is the bug this check was written for.")
        return 1

    print(f"site coverage: OK — {len(required(career))} items from career.json all "
          f"present across {len(pages)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
