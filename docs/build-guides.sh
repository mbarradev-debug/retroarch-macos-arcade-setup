#!/usr/bin/env bash
# Regenerate every PDF guide in docs/guides/ from the Markdown in docs/guides/src/.
#
# Needs Node.js 18+ and Google Chrome. The first run installs the two build
# dependencies (marked, playwright-core) into docs/node_modules. If pdfinfo is
# available (brew install poppler), each PDF is checked to have exactly one page.
set -euo pipefail

cd "$(dirname "$0")"

command -v node >/dev/null || { echo "Error: Node.js is required (brew install node)." >&2; exit 1; }
[[ -d "/Applications/Google Chrome.app" ]] || { echo "Error: Google Chrome is required to render the PDFs." >&2; exit 1; }
[[ -d node_modules ]] || npm ci --no-audit --no-fund

node build-guides.mjs

if command -v pdfinfo >/dev/null; then
  for pdf in guides/*.pdf; do
    pages=$(pdfinfo "$pdf" | awk '/^Pages:/ {print $2}')
    [[ "$pages" == 1 ]] || { echo "Error: $pdf has $pages pages." >&2; exit 1; }
  done
  echo "All guides are single-page PDFs."
fi
