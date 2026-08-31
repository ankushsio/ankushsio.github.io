#!/usr/bin/env bash
#
# Compatibility shim. The publish step now lives in publish_resume_pdf.py and runs as
# site/package.json's `postbuild` hook, so nothing in this repo calls this file.
#
# It exists because the Cloudflare build command still invokes it by name, and removing
# the script without editing that command failed a build whose real work had already
# succeeded. A stale build command should not be able to fail a good build -- that field
# has been the single least reliable part of this pipeline.
#
# Safe to run twice: the hook has normally already produced the PDF, and re-rendering the
# same inputs produces the same output.
#
# Once the dashboard command drops this step, delete this file.
#
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec python scripts/publish_resume_pdf.py
