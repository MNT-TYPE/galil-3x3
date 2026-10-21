#!/bin/sh
# Rebuilds the parents' view-only page into docs/ and pushes it to GitHub Pages.
# Usage: tools/publish.sh [backup.json]
#   - with no argument: uses seed.json
#   - with a file: uses a backup exported from the app (ניהול → גיבוי), and copies it over seed.json
set -e
cd "$(dirname "$0")/.."
DATA="${1:-seed.json}"
if [ "$DATA" != "seed.json" ]; then cp "$DATA" seed.json; fi
REMOTE="$(git remote get-url origin 2>/dev/null || true)"
SLUG="$(printf '%s' "$REMOTE" | sed -E 's#.*github\.com[:/]([^/]+)/([^/.]+)(\.git)?$#\1/\2#')"
if [ -n "$SLUG" ] && [ "$SLUG" != "$REMOTE" ]; then
  SHARE="https://$(printf '%s' "$SLUG" | tr 'A-Z' 'a-z' | sed -E 's#([^/]+)/(.+)#\1.github.io/\2/#')"
  python3 tools/build_static.py --data seed.json --out docs --github "$SLUG@main:docs/data.json" --share-url "$SHARE"
else
  SHARE=""; python3 tools/build_static.py --data seed.json --out docs
fi
git add -A
git commit -m "Update tournament board $(date '+%Y-%m-%d %H:%M')" || echo "nothing changed"
if [ -n "$REMOTE" ]; then git push; echo "Published. Parents' link: ${SHARE:-see your GitHub Pages settings}"; else echo "No git remote yet: see README for the one-time GitHub setup."; fi
