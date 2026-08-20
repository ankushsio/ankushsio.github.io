"""
Fail the build when a résumé variant contradicts content/career.json.

    python scripts/check_resume_consistency.py

Why this exists
---------------
resume/variants/*.json is a second source of truth. It carries its own target_role,
summary and skill rows rather than reading career.json, because the one-page résumé is
tailored -- it abbreviates, reorders and drops things the site keeps. That freedom is
deliberate, but it means the variant can quietly disagree with career.json, and only the
variant reaches the PDF.

It has done exactly that twice:

  * `Go` was removed from career.json but left in the variant, so the shipped PDF kept
    listing a language the site and LinkedIn no longer claimed.
  * The title was changed to Senior Software Engineer everywhere except the variant, so
    the PDF header still read Senior Backend Engineer after the site said otherwise.

Both were caught by a human reading the PDF, which is the wrong last line of defence for
a document sent to recruiters.

What is and is not enforced
---------------------------
Enforced, because these are unambiguous:

  * target_role must equal person.title
  * every project slug a variant references must still exist in career.json
  * every project label must match that project's title
  * every language listed on the résumé must be a skill career.json actually claims

Not enforced: the rest of the skill rows. The variant writes "GCP Pub/Sub" where
career.json says "Google Cloud Platform (GCP)" and "OCR/HTR" for "OCR / handwriting
recognition". Comparing those needs a synonym table that would rot faster than the thing
it guards, and a check that cries wolf gets ignored.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAREER = ROOT / "content" / "career.json"
VARIANTS = ROOT / "resume" / "variants"


def tokens(skill: str) -> set[str]:
    """Split a skill into comparable pieces.

    "TypeScript/Node.js" -> {"typescript", "node.js"} so it matches career.json listing
    TypeScript and JavaScript/Node.js separately. Parentheticals are dropped:
    "GCP (Cloud Run)" -> {"gcp"}. Splitting is on separators only -- never on spaces --
    so short names stay whole and "Go" cannot be satisfied by "Google Cloud Platform".
    """
    skill = re.sub(r"\([^)]*\)", " ", skill)
    parts = re.split(r"[/,&]| and ", skill)
    return {p.strip().lower() for p in parts if p.strip()}


def language_row(variant: dict) -> list[str] | None:
    for row in variant.get("skill_rows", []):
        if "lang" in str(row.get("label", "")).lower():
            return row.get("items") or []
    return None


def main() -> int:
    career = json.loads(CAREER.read_text(encoding="utf-8"))
    person = career["person"]
    projects = {p["slug"]: p for c in career["companies"] for p in c["projects"]}

    claimed: set[str] = set()
    for group in career["skills"].values():
        for skill in group:
            claimed |= tokens(skill)

    files = sorted(VARIANTS.glob("*.json"))
    if not files:
        print("ERROR: no résumé variants found", file=sys.stderr)
        return 1

    problems: list[str] = []
    for path in files:
        name = path.relative_to(ROOT).as_posix()
        v = json.loads(path.read_text(encoding="utf-8"))

        role = v.get("target_role")
        if role != person["title"]:
            problems.append(
                f"{name}: target_role is {role!r} but person.title is "
                f"{person['title']!r}.\n"
                f"    Only the variant reaches the PDF, so the résumé would ship the "
                f"wrong title while the site shows the right one."
            )

        def check_projects(node):
            if isinstance(node, dict):
                slug = node.get("project")
                if slug:
                    if slug not in projects:
                        problems.append(
                            f"{name}: references project {slug!r}, which no longer "
                            f"exists in career.json (renamed or removed)."
                        )
                    elif "label" in node and node["label"] != projects[slug]["title"]:
                        problems.append(
                            f"{name}: project {slug!r} is labelled "
                            f"{node['label']!r} but career.json titles it "
                            f"{projects[slug]['title']!r}."
                        )
                for x in node.values():
                    check_projects(x)
            elif isinstance(node, list):
                for x in node:
                    check_projects(x)

        check_projects(v)

        langs = language_row(v)
        if langs is None:
            problems.append(f"{name}: no Languages row found in skill_rows.")
        else:
            for lang in langs:
                unknown = tokens(lang) - claimed
                if unknown:
                    problems.append(
                        f"{name}: résumé lists {lang!r} but career.json claims no "
                        f"skill matching {sorted(unknown)}.\n"
                        f"    Either add it to career.json or drop it from the "
                        f"résumé -- the PDF should not claim more than the site."
                    )

    if problems:
        print(f"résumé consistency: FAILED - {len(problems)} disagreement(s) with "
              f"career.json\n", file=sys.stderr)
        for p in problems:
            print(f"  - {p}\n", file=sys.stderr)
        return 1

    print(f"résumé consistency: OK - {len(files)} variant(s) agree with career.json "
          f"on title, projects and languages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
