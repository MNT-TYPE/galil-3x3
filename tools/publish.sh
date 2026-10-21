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
SHARE=""
case "$REMOTE" in
  *github.com*) SHARE="$(printf '%s' "$REMOTE" | sed -E 's#.*github\.com[:/]([^/]+)/([^/.]+)(\.git)?$#https://\1.github.io/\2/#' | tr 'A-Z' 'a-z')";;
esac
if [ -n "$SHARE" ]; then python3 tools/build_static.py --data seed.json --out docs/index.html --share-url "$SHARE"
else python3 tools/build_static.py --data seed.json --out docs/index.html; fi
git add -A
git commit -m "Update tournament board $(date '+%Y-%m-%d %H:%M')" || echo "nothing changed"
if [ -n "$REMOTE" ]; then git push; echo "Published. Parents' link: ${SHARE:-see your GitHub Pages settings}"; else echo "No git remote yet: see README for the one-time GitHub setup."; fi
