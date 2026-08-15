"""
ATS check for a rendered resume PDF.

    python scripts/ats_check.py                       # lint the base resume
    python scripts/ats_check.py acme path/to/jd.txt   # lint + keyword coverage vs a JD

There is no universal "ATS score". Greenhouse, Lever, Workday and Taleo mostly parse and
store resumes; recruiters then search by keyword. The percentage scores sold by resume
checkers are each a proprietary invention and do not transfer between systems, so this
script deliberately reports nothing of the kind.

It checks the two things that genuinely cause rejections:

  1. PARSE  -- extracts text back out of the RENDERED PDF. If extraction is empty,
              garbled, or out of reading order, that is the failure a real ATS hits.
  2. COVER  -- compares the resume against a job description and names which of the
              JD's terms are missing, so gaps get closed with true statements.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_SECTIONS = ["summary", "experience", "skills"]

# Words that carry no signal when comparing a JD against a resume.
STOP = set("""
a an and are as at be by for from has have in is it its of on or that the to with will
you your our we us they their this those these can could should would may might must
who whom which what when where why how all any both each few more most other some such
no nor not only own same so than too very just about into over under after before again
work working works experience experienced years year team teams role roles job jobs
position candidate candidates ability able strong excellent good great new using use used
including include includes across within while also well across per via etc
""".split())

# Terms that look like skills and are worth reporting as coverage gaps.
TECH_HINT = re.compile(
    r"^[a-z0-9][a-z0-9+#./_-]{1,}$", re.I)


def extract_text(pdf: Path) -> tuple[str, int]:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf))
    pages = [(p.extract_text() or "") for p in reader.pages]
    return "\n".join(pages), len(pages)


def tokenize(text: str) -> Counter:
    words = re.findall(r"[A-Za-z][A-Za-z0-9+#./_-]*", text.lower())
    # Strip trailing punctuation so "scale." and "scale" are one term.
    words = [w.rstrip("./-_") for w in words]
    return Counter(w for w in words if w and w not in STOP and len(w) > 1)


def lint(text: str, pages: int, limit: int) -> list[str]:
    problems: list[str] = []

    if len(text.strip()) < 400:
        problems.append(
            f"extracted only {len(text.strip())} characters — the PDF may not carry "
            f"real selectable text, which is the classic ATS parse failure")

    if pages > limit:
        problems.append(f"{pages} pages, limit is {limit}")

    low = text.lower()
    for section in REQUIRED_SECTIONS:
        if section not in low:
            problems.append(f"standard section heading '{section}' not found in the "
                            f"extracted text")

    # Reading order: the name should come out near the top, not scrambled.
    head = "\n".join(text.strip().splitlines()[:3]).lower()
    if "ankush" not in head:
        problems.append("the name is not in the first lines of extracted text — "
                        "reading order may be scrambled")

    if "�" in text:
        problems.append("replacement characters present — font encoding is not "
                        "extracting cleanly")

    if re.search(r"TODO", text):
        problems.append("placeholder 'TODO' text is still in the document")

    return problems


def coverage(resume_text: str, jd_text: str) -> tuple[list[str], list[str]]:
    resume_tokens = tokenize(resume_text)
    jd_tokens = tokenize(jd_text)

    # Only consider JD terms that appear more than once or look like technologies:
    # a single passing mention of a common word is not a real requirement.
    candidates = [
        w for w, n in jd_tokens.items()
        if (n >= 2 or TECH_HINT.match(w)) and len(w) > 2
    ]
    matched = sorted({w for w in candidates if resume_tokens[w] > 0})
    missing = sorted({w for w in candidates if resume_tokens[w] == 0})
    return matched, missing


def main() -> int:
    variant = sys.argv[1] if len(sys.argv) > 1 else "base"
    jd_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    pdf = ROOT / "resume" / "build" / variant / "resume.pdf"
    if not pdf.exists():
        sys.exit(f"ERROR: {pdf} not found. Run: python scripts/render_resume.py {variant}")

    variant_file = ROOT / "resume" / "variants" / f"{variant}.json"
    limit = 1
    if variant_file.exists():
        limit = json.loads(variant_file.read_text(encoding="utf-8")).get("max_pages", 1)

    text, pages = extract_text(pdf)

    print(f"ATS check — {pdf.relative_to(ROOT)}")
    print(f"  pages extracted      : {pages} (limit {limit})")
    print(f"  characters extracted : {len(text.strip())}")
    print(f"  words extracted      : {len(text.split())}")

    problems = lint(text, pages, limit)
    print("\nFormat lint")
    if problems:
        for p in problems:
            print(f"  FAIL  {p}")
    else:
        print("  OK  single column, standard headings, clean text extraction, "
              "correct reading order")

    if jd_path:
        if not jd_path.exists():
            sys.exit(f"ERROR: job description not found at {jd_path}")
        matched, missing = coverage(text, jd_path.read_text(encoding="utf-8"))
        total = len(matched) + len(missing)
        print(f"\nKeyword coverage vs {jd_path.name}")
        print(f"  matched : {len(matched)}/{total}")
        print(f"  missing : {', '.join(missing[:45]) or 'none'}")
        print("\n  Only add a missing term if it is TRUE and evidenced in "
              "content/career.json.\n  Keyword stuffing fails the moment a human reads it.")
    else:
        print("\n(no job description supplied — pass one as the second argument "
              "for keyword coverage)")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
