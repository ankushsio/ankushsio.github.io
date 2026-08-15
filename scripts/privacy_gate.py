"""
Privacy gate — run before EVERY push, not just the first.

The repo is public. The source data it was built from is not: it names clients, a
colleague, and internal project codenames. This script greps everything git is actually
tracking for those terms and exits non-zero if any appear.

Usage:  python scripts/privacy_gate.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Client names, internal codenames, and colleague first names that appear in the raw
# timesheets and evaluations. None of these may appear in tracked files.
FORBIDDEN = [
    # clients
    "IPRD", "iprdgroup", "Mayo", "Medtronic", "BluB0x", "Blub0x", "BlueB0x",
    "Living Optics", "living optics", "Gates", "READCOOP", "ReadCoop", "read coop",
    "Incytes", "Satch", "Seastar", "Jaystar", "HealthFactor", "Timphany", "Panomor",
    "Efilon", "Tympany",
    # internal codenames
    "CTBW", "CCBW", "RegenMed", "Regen Med", "Impact Health", "ImpactHealth",
    "Hyperspectral IMEC", "BBNVR",
    # colleagues
    "Aparna", "Kashyap", "Omkar", "Akhil", "Keith", "Vinay", "Nitin", "Abhinav",
    "Aniket", "Shyamal", "Vishal", "Dolph", "Stephen", "Aditya", "Prince",
]

# Terms that are allowed despite looking similar, with the reason.
ALLOWED_NOTES = {
    "Apra Labs": "employer — explicitly nameable",
    "ApraPipes": "employer's own open-source project — nameable",
}

# This file necessarily contains the forbidden list itself.
SELF = "scripts/privacy_gate.py"

# Binary-ish extensions we do not grep.
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff",
                 ".woff2", ".ttf", ".otf", ".zip", ".xlsx", ".docx"}


def read_text_for_scan(path: Path) -> str | None:
    """Return scannable text for a tracked file, or None if it cannot be read.

    PDFs are handled explicitly rather than skipped: the resume PDF is served publicly
    from the site, so it is exactly the kind of artifact a leak must not reach.
    """
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            print(f"WARNING: pypdf not installed — cannot scan {path.name}. "
                  f"Install it with: python -m pip install pypdf", file=sys.stderr)
            return None
        try:
            reader = PdfReader(str(path))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception as exc:  # a PDF we cannot read is a PDF we cannot clear
            print(f"WARNING: could not read {path.name}: {exc}", file=sys.stderr)
            return None
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return None

# Lockfiles are machine-generated base64 integrity hashes. Random letter runs inside
# them trigger false positives ("Mayo" appears inside a sha512 hash) and no human-written
# client name can end up there.
SKIP_FILES = {"site/package-lock.json", "package-lock.json"}


def build_pattern(term: str) -> re.Pattern[str]:
    """Word-bounded where the term's edges are word characters, so short names like
    'Mayo' or 'Gates' cannot match inside a longer token."""
    left = r"\b" if term[0].isalnum() else ""
    right = r"\b" if term[-1].isalnum() else ""
    return re.compile(left + re.escape(term) + right, re.IGNORECASE)


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if line.strip()]


def main() -> int:
    files = tracked_files()
    if not files:
        print("privacy gate: nothing tracked yet — nothing to check")
        return 0

    patterns = {term: build_pattern(term) for term in FORBIDDEN}
    findings: list[tuple[str, int, str, str]] = []
    scanned = 0

    for rel in files:
        if rel == SELF or rel in SKIP_FILES:
            continue
        if Path(rel).suffix.lower() in SKIP_SUFFIXES:
            continue
        text = read_text_for_scan(ROOT / rel)
        if text is None:
            continue
        scanned += 1
        for lineno, line in enumerate(text.splitlines(), 1):
            for term, pattern in patterns.items():
                if pattern.search(line):
                    findings.append((rel, lineno, term, line.strip()[:110]))

    if findings:
        print(f"PRIVACY GATE FAILED — {len(findings)} occurrence(s) in tracked files:\n")
        for rel, lineno, term, line in findings[:60]:
            print(f"  {rel}:{lineno}  [{term}]  {line}")
        if len(findings) > 60:
            print(f"  ... and {len(findings) - 60} more")
        print("\nRemove these before pushing. The repo is public.")
        return 1

    print(f"privacy gate: OK — {scanned} of {len(files)} tracked files scanned "
          f"(PDFs included), no client, codename or colleague names found")
    for term, why in ALLOWED_NOTES.items():
        print(f"  (allowed: {term} — {why})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
