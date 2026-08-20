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
  * every highlight id a variant references must still exist in career.json
  * every language listed on the résumé must be a skill career.json actually claims

The highlight-id rule was added after removing a Deloitte bullet from career.json left
two dangling references in the variant -- one in a selection list, one in a prior_text
override. render_resume.py did fail loudly on the first, but nothing in CI runs it,
because the PDF is committed rather than built. So the résumé would have stayed
unbuildable without anything going red.

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


def show_overrides(career: dict, files: list[Path]) -> int:
    """Print every résumé bullet that rewords a career.json highlight, side by side.

    Overrides exist so the one-page résumé can say the same thing in fewer words, and
    that is legitimate -- which is exactly why drift hides here. "Cut" for "Reduced" is
    fine; "each new EHR integration" after career.json dropped the EHR framing is not.
    No checker can tell those apart, so this prints them for a human instead of guessing.
    """
    canon: dict[str, str] = {}

    def collect(n):
        if isinstance(n, dict):
            if isinstance(n.get("id"), str) and isinstance(n.get("text"), str):
                canon[n["id"]] = n["text"]
            for x in n.values():
                collect(x)
        elif isinstance(n, list):
            for x in n:
                collect(x)

    collect(career)

    for path in files:
        v = json.loads(path.read_text(encoding="utf-8"))
        print(f"=== {path.name} ===")
        for section in v.get("sections", []):
            for b in section.get("bullets", []):
                if isinstance(b, dict) and "text" in b:
                    print(f"\n  {b['id']}")
                    print(f"    career : {canon.get(b['id'], '<<missing>>')}")
                    print(f"    résumé : {b['text']}")
        for k, text in v.get("prior_text", {}).items():
            print(f"\n  {k}")
            print(f"    career : {canon.get(k, '<<missing>>')}")
            print(f"    résumé : {text}")
    return 0


def main() -> int:
    career = json.loads(CAREER.read_text(encoding="utf-8"))
    person = career["person"]
    projects = {p["slug"]: p for c in career["companies"] for p in c["projects"]}

    # Every highlight id anywhere in career.json: project highlights, cross-project
    # highlights, and the prior roles and internships.
    known_ids: set[str] = set()

    def collect(node):
        if isinstance(node, dict):
            if "id" in node and "text" in node and isinstance(node["id"], str):
                known_ids.add(node["id"])
            for v in node.values():
                collect(v)
        elif isinstance(node, list):
            for v in node:
                collect(v)

    collect(career)

    claimed: set[str] = set()
    for group in career["skills"].values():
        for skill in group:
            claimed |= tokens(skill)

    files = sorted(VARIANTS.glob("*.json"))
    if not files:
        print("ERROR: no résumé variants found", file=sys.stderr)
        return 1

    if "--overrides" in sys.argv:
        return show_overrides(career, files)

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

        # A stale id makes render_resume.py refuse to build the PDF, and nothing in CI
        # runs it -- the PDF is committed, not built -- so the résumé can sit unbuildable
        # with everything green.
        #
        # Ids appear in two shapes. Bullets are objects, {"id": "ctp-deploy", "text":
        # "..."}, so the id is a key rather than a bare string in a list. prior_text
        # inverts that: the id is the key and the override text is the value.
        referenced: set[str] = set()
        for section in v.get("sections", []):
            for bullet in section.get("bullets", []):
                if isinstance(bullet, dict) and isinstance(bullet.get("id"), str):
                    referenced.add(bullet["id"])
        referenced |= {k for k in v.get("prior_text", {}) if isinstance(k, str)}
        for ref in sorted(referenced - known_ids - set(projects)):
            problems.append(
                f"{name}: references highlight id {ref!r}, which no longer exists in "
                f"career.json.\n"
                f"    render_resume.py will refuse to build the PDF until this is "
                f"removed or the highlight is restored."
            )

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
