"""
Render a one-page resume PDF from content/career.json plus a variant file.

    python scripts/render_resume.py                  # renders the base variant
    python scripts/render_resume.py acme             # renders resume/variants/acme.json

Outputs to resume/build/<variant>/resume.pdf and asserts the page count.

The variant chooses which highlights appear and may REWRITE their wording to match a
job description -- but every bullet must reference a highlight id that exists in
career.json. Unknown ids are a hard error. That is the mechanism that keeps tailored
resumes honest: the phrasing is free, the underlying claim is not.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAREER = ROOT / "content" / "career.json"
RESUME = ROOT / "resume"
TEMPLATE = RESUME / "template.typ"

SKILL_LABELS = {
    "languages": "Languages",
    "backend": "Backend & messaging",
    "databases": "Databases",
    "cloud_devops": "Cloud & DevOps",
    "domain": "Healthcare & standards",
    "security": "Security",
    "ml_imaging": "ML & imaging",
    "practices": "Practices",
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def typst_bin() -> str:
    found = shutil.which("typst")
    if found:
        return found
    # winget puts shims here and they are not always on PATH in a fresh shell
    fallback = Path.home() / "AppData/Local/Microsoft/WinGet/Links/typst.exe"
    if fallback.exists():
        return str(fallback)
    sys.exit("ERROR: typst not found. Install with: winget install Typst.Typst")


def fmt_month(ym: str | None, *, fallback: str = "Present") -> str:
    """'2024-11' -> 'Nov 2024'. Consistent dates matter to resume parsers."""
    if not ym:
        return fallback
    year, month = ym.split("-")[:2]
    return f"{MONTHS[int(month) - 1]} {year}"


def fmt_range(period: dict) -> str:
    return f"{fmt_month(period['start'])} – {fmt_month(period.get('end'))}"


def build_data(career: dict, variant: dict) -> dict:
    person = career["person"]
    company = career["companies"][0]
    projects = {p["slug"]: p for p in company["projects"]}
    highlights = {
        h["id"]: h
        for p in company["projects"]
        for h in p["highlights"]
    }
    highlights.update({h["id"]: h for h in company["cross_project_highlights"]})

    # --- contact line ---------------------------------------------------------
    contact: list[str] = []
    for value in (person.get("email"), person.get("location")):
        if value and not str(value).startswith("TODO"):
            contact.append(str(value))
    for _, url in (person.get("links") or {}).items():
        if url and not str(url).startswith("TODO"):
            contact.append(str(url).replace("https://", ""))
    if not contact:
        contact = ["TODO: email", "TODO: location", "TODO: linkedin"]

    # --- experience -----------------------------------------------------------
    groups = []
    for section in variant["sections"]:
        project = projects.get(section["project"])
        if project is None:
            sys.exit(f"ERROR: variant references unknown project "
                     f"'{section['project']}'")
        bullets = []
        for entry in section["bullets"]:
            hid = entry["id"]
            if hid not in highlights:
                sys.exit(f"ERROR: variant references unknown highlight id '{hid}'. "
                         f"Every bullet must trace to content/career.json.")
            # A variant may rewrite wording for a JD; the claim stays anchored.
            bullets.append(entry.get("text") or highlights[hid]["text"])
        groups.append({
            "label": section.get("label", project["title"]),
            "dates": fmt_range(project["period"]),
            "bullets": bullets,
        })

    experience = [{
        "company": company["name"],
        "role": company["role"],
        "dates": f"{fmt_month(company['start'][:7])} – "
                 f"{fmt_month(company.get('end'))}",
        "note": company.get("context_short") or company.get("context", ""),
        "groups": groups,
    }]

    for job in career.get("prior_experience", {}).get("full_time", []):
        experience.append(job)

    # --- skills ---------------------------------------------------------------
    skills = [
        {"label": SKILL_LABELS.get(key, key.title()),
         "items": ", ".join(career["skills"][key])}
        for key in variant["skills"]
        if key in career["skills"]
    ]

    education = career.get("education", {})
    education_rows = education if isinstance(education, list) else []

    return {
        "name": person["name"],
        "title": variant.get("target_role", person["title"]),
        "contact": contact,
        "summary": variant["summary"],
        "experience": experience,
        "skills": skills,
        "education": education_rows,
    }


def main() -> int:
    name = sys.argv[1] if len(sys.argv) > 1 else "base"
    variant_path = RESUME / "variants" / f"{name}.json"
    if not variant_path.exists():
        sys.exit(f"ERROR: no variant at {variant_path}")

    career = json.loads(CAREER.read_text(encoding="utf-8"))
    variant = json.loads(variant_path.read_text(encoding="utf-8"))

    out_dir = RESUME / "build" / name
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "data.json").write_text(
        json.dumps(build_data(career, variant), indent=2), encoding="utf-8")
    shutil.copyfile(TEMPLATE, out_dir / "template.typ")

    pdf = out_dir / "resume.pdf"
    result = subprocess.run(
        [typst_bin(), "compile", "template.typ", "resume.pdf"],
        cwd=out_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return 1

    # --- the hard constraint --------------------------------------------------
    from pypdf import PdfReader

    pages = len(PdfReader(str(pdf)).pages)
    limit = variant.get("max_pages", 1)
    print(f"rendered {pdf.relative_to(ROOT)}  —  {pages} page(s)")

    if pages > limit:
        print(f"\nFAIL: {pages} pages, limit is {limit}.")
        print("Fix by cutting the weakest bullet, then tightening wording. Do not "
              "shrink type below 10pt or margins below 0.5in to force a fit.")
        return 1

    print(f"OK: within the {limit}-page limit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
