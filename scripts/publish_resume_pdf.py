"""Put the phone-number résumé on the live site WITHOUT putting the number in git.

Runs as site/package.json's `postbuild` hook, so it fires on any build that runs
`npm --prefix site run build` -- which is every build. That placement is deliberate: it
was previously a step in the Cloudflare build command, and four consecutive builds ran
with a stale copy of that command, so the step never executed and the site quietly served
the phone-free PDF. A hook inside the repo cannot be missed that way.

    Turn it on : set RESUME_PHONE in the Cloudflare Workers Builds environment.
    Turn it off: delete RESUME_PHONE and redeploy. The committed phone-free PDF ships
                 instead, and nothing needs scrubbing anywhere.

The number never enters git. site/public/ankush-jain-resume.pdf is tracked in a public
repo, so a --phone build committed there would sit in the history for good and a takedown
could not reach it. This writes into site/dist, which is gitignored and is what wrangler
uploads, and never touches site/public -- so the privacy gate has nothing to trip on.

Python rather than shell so it behaves the same on the Linux builder and on Windows,
where the postbuild hook also runs.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST_PDF = ROOT / "site" / "dist" / "ankush-jain-resume.pdf"
BUILT_PDF = ROOT / "resume" / "build" / "base" / "resume.pdf"
TYPST_VERSION = os.environ.get("TYPST_VERSION", "0.15.1")
TYPST_DIR = ROOT / ".typst"

TAG = "publish_resume_pdf:"


def log(msg: str) -> None:
    # Flushed: npm interleaves hook output with the build log, and an unflushed line can
    # land after the lines that explain it.
    print(f"{TAG} {msg}", flush=True)


def ensure_typst() -> str:
    """Return a typst binary path, downloading the pinned release if the host lacks one.

    Pinned, because an unpinned toolchain silently changing the layout of a one-page
    résumé is exactly the kind of drift nobody notices.
    """
    found = shutil.which("typst") or shutil.which("typst", path=str(TYPST_DIR))
    if found:
        return found
    if not sys.platform.startswith("linux"):
        sys.exit(f"{TAG} ERROR - typst not found and this host is not Linux. "
                 f"Install it locally: winget install Typst.Typst")

    url = (f"https://github.com/typst/typst/releases/download/v{TYPST_VERSION}"
           f"/typst-x86_64-unknown-linux-musl.tar.xz")
    log(f"fetching typst {TYPST_VERSION}")
    TYPST_DIR.mkdir(exist_ok=True)
    archive = TYPST_DIR / "typst.tar.xz"
    urllib.request.urlretrieve(url, archive)
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            if Path(member.name).name == "typst":
                member.name = "typst"
                # filter="data" is the 3.14 default and silences its DeprecationWarning;
                # keyword-guarded because it does not exist before 3.12.
                try:
                    tar.extract(member, TYPST_DIR, filter="data")
                except TypeError:
                    tar.extract(member, TYPST_DIR)
                break
        else:
            sys.exit(f"{TAG} ERROR - no typst binary inside {url}")
    binary = TYPST_DIR / "typst"
    binary.chmod(0o755)
    return str(binary)


def main() -> int:
    phone = os.environ.get("RESUME_PHONE", "").strip()
    # Printed unconditionally. The whole point of this line is that a misconfiguration
    # stops looking exactly like a success.
    log(f"RESUME_PHONE visible to build: {'yes' if phone else 'no'}")
    if not phone:
        log("shipping the committed phone-free PDF")
        return 0

    if not DIST_PDF.exists():
        log(f"ERROR - {DIST_PDF.relative_to(ROOT)} not found; did the site build run?")
        return 1

    typst = ensure_typst()
    env = {**os.environ, "PATH": f"{Path(typst).parent}{os.pathsep}{os.environ['PATH']}"}
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "render_resume.py"), "--phone"],
        cwd=ROOT, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout, flush=True)
        print(result.stderr, file=sys.stderr, flush=True)
        log("ERROR - render failed (the one-page assertion also lives in there)")
        return 1

    shutil.copyfile(BUILT_PDF, DIST_PDF)

    # Verify rather than assume: a silent failure here leaves the site advertising a
    # phone number it does not carry, which is worse than not shipping one.
    from pypdf import PdfReader

    text = "\n".join((p.extract_text() or "") for p in PdfReader(str(DIST_PDF)).pages)
    digits = "".join(c for c in phone if c.isdigit())
    if digits and digits[-6:] not in "".join(c for c in text if c.isdigit()):
        log("ERROR - phone number is not in the rendered PDF")
        return 1
    log("OK - hosted PDF carries the phone number")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
