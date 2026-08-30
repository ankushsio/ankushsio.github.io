#!/usr/bin/env bash
#
# Put the phone-number résumé on the live site WITHOUT putting the number in git.
#
# The repo is public and site/public/ankush-jain-resume.pdf is a tracked file, so a phone
# number committed there would sit in the history for good -- a takedown would stop new
# downloads and change nothing else. Instead the number arrives as a build environment
# variable and this script writes the rendered PDF straight into site/dist, which is
# gitignored and is what wrangler uploads.
#
#   Turn it on : set RESUME_PHONE in the Cloudflare Workers Builds environment.
#   Turn it off: delete RESUME_PHONE and redeploy. The committed phone-free PDF ships
#                instead, and nothing needs to be scrubbed anywhere.
#
# Run it AFTER `npm --prefix site run build`: it overwrites the copy Astro placed in dist.
# It deliberately never touches site/public, so the privacy gate has nothing to trip on and
# no ordering constraint exists between the two.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DIST_PDF="site/dist/ankush-jain-resume.pdf"
TYPST_VERSION="${TYPST_VERSION:-0.15.1}"

if [ -z "${RESUME_PHONE:-}" ]; then
  echo "publish_resume_pdf: RESUME_PHONE unset — shipping the committed phone-free PDF"
  exit 0
fi

if [ ! -f "$DIST_PDF" ]; then
  echo "publish_resume_pdf: ERROR — $DIST_PDF not found. Run the site build first." >&2
  exit 1
fi

# Typst is a single static binary. Pinned, because an unpinned toolchain silently changing
# the layout of a one-page résumé is exactly the kind of drift nobody notices.
if ! command -v typst >/dev/null 2>&1; then
  echo "publish_resume_pdf: fetching typst ${TYPST_VERSION}"
  url="https://github.com/typst/typst/releases/download/v${TYPST_VERSION}/typst-x86_64-unknown-linux-musl.tar.xz"
  mkdir -p .typst
  curl -fsSL "$url" | tar -xJ -C .typst --strip-components=1
  export PATH="$ROOT/.typst:$PATH"
fi

python scripts/render_resume.py           # page-count assertion still applies
python scripts/render_resume.py --phone   # same variant, phone in the contact line
cp resume/build/base/resume.pdf "$DIST_PDF"

# Verify rather than assume: a silent failure here means the site advertises a phone number
# it does not carry, which is worse than not shipping one.
python - "$DIST_PDF" <<'PY'
import os, re, sys
from pypdf import PdfReader

text = "\n".join((p.extract_text() or "") for p in PdfReader(sys.argv[1]).pages)
digits = re.sub(r"\D", "", os.environ["RESUME_PHONE"])
if digits and digits[-6:] not in re.sub(r"[^\d]", "", text):
    sys.exit("publish_resume_pdf: ERROR — phone number is not in the rendered PDF")
print("publish_resume_pdf: OK — hosted PDF carries the phone number")
PY
