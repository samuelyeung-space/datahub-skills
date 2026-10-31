#!/usr/bin/env bash
# Publish ONLY the four public web assets to the existing Cloudflare Pages Direct Upload project.
# Requires a pre-existing Wrangler OAuth login or Cloudflare credentials in environment.
# Does not read or print credentials. Does not upload Git files, source archives, or user data.
set -euo pipefail
SITE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT="ai-handout-school"
for f in index.html app.js ai.txt _headers; do
  if [[ ! -f "$SITE_DIR/$f" ]]; then
    printf 'Required site file missing: %s\n' "$f" >&2
    exit 1
  fi
done
if ! command -v npx >/dev/null 2>&1; then
  printf 'Node.js and npm/npx are required to run Wrangler.\n' >&2
  exit 1
fi
DIST="$(mktemp -d)"
trap 'rm -rf -- "$DIST"' EXIT
cp -- "$SITE_DIR/index.html" "$SITE_DIR/app.js" "$SITE_DIR/ai.txt" "$SITE_DIR/_headers" "$DIST/"
if [[ -f "$SITE_DIR/404.html" ]]; then
  cp -- "$SITE_DIR/404.html" "$DIST/"
fi
printf 'Deploying approved public assets to Cloudflare Pages project: %s\n' "$PROJECT"
printf 'Assets: index.html, app.js, ai.txt, _headers%s\n' "$([[ -f "$DIST/404.html" ]] && printf ', 404.html' || true)"
# Cloudflare's existing Direct Upload projects are deployed with Wrangler.
# Do not run this without authenticating Wrangler to the intended Cloudflare account.
npx wrangler pages deploy "$DIST" --project-name="$PROJECT" --branch=main
printf '\nVerify the live site and machine-readable entry:\n'
printf '  https://ai-handout-school.pages.dev/\n  https://ai-handout-school.pages.dev/ai.txt\n'
