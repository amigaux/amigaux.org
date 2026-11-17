#!/bin/bash
# Build the site and deploy it to amigaux.org (rsync over ssh, no root), then verify it is served.
#
#   DEPLOY_HOST=<ssh target> DEPLOY_DEST=<docroot> ./deploy.sh [--dry-run] [--allow-placeholders]
#   DEPLOY_HOST=<ssh target> DEPLOY_DEST=<docroot>/preview ./deploy.sh --preview [--dry-run]
#
#   DEPLOY_HOST   required: the ssh target (user@host, or a Host from ~/.ssh/config)
#   DEPLOY_DEST   required: the site's docroot on that host
#   DEPLOY_URL    the page fetched after the sync (default https://amigaux.org/, or
#                 https://amigaux.org/preview/ with --preview)
#   MKDOCS        the mkdocs to build with (default: mkdocs on PATH; pip install -r requirements.txt)
#   MAN_PKGS, AMIX, AMIX_REF   the release's packages and pin, for the man pages (tools/build.sh)
#
#   --dry-run             build and check, then show what rsync would change; write nothing
#   --allow-placeholders  deploy even though a page carries a PLACEHOLDER marker; only on purpose
#   --preview             the unlinked preview (tools/build.sh --preview: noindex, a banner,
#                         placeholders as TBD) into DEPLOY_DEST, which must end in /preview
#
# The build is tools/build.sh: MkDocs into build/site/, then tools/check-site.py, which refuses
# placeholders, third-party loads and broken internal links before anything is sent.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

DRY=()
CHECK=()
PREVIEW=
for arg in "$@"; do
    case "$arg" in
        --dry-run|-n) DRY=(-n) ;;
        --allow-placeholders) CHECK=(--allow-placeholders) ;;
        --preview) PREVIEW=1 ;;
        *) echo "usage: DEPLOY_HOST=... DEPLOY_DEST=... $0 [--preview] [--dry-run] [--allow-placeholders]" >&2; exit 1 ;;
    esac
done
[[ -n "${DEPLOY_HOST:-}" ]] || { echo "deploy: DEPLOY_HOST is not set (the ssh target)" >&2; exit 1; }
[[ -n "${DEPLOY_DEST:-}" ]] || { echo "deploy: DEPLOY_DEST is not set (the docroot on $DEPLOY_HOST)" >&2; exit 1; }
if [[ -n "$PREVIEW" ]]; then
    # The preview syncs with --delete too: aimed at the docroot it would wipe the live site.
    [[ "${DEPLOY_DEST%/}" == */preview ]] || { echo "deploy: --preview needs DEPLOY_DEST ending in /preview" >&2; exit 1; }
    [[ ${#CHECK[@]} -eq 0 ]] || { echo "deploy: --preview shows placeholders as TBD; no --allow-placeholders" >&2; exit 1; }
    CHECK=(--preview)
    URL="${DEPLOY_URL:-https://amigaux.org/preview/}"
else
    URL="${DEPLOY_URL:-https://amigaux.org/}"
fi

# One build or deploy at a time in this checkout, held from the build to the end of the sync, so
# another build cannot change build/site under the sync. tools/build.sh sees it is held for it.
if command -v flock >/dev/null; then
    mkdir -p "$HERE/build"
    exec 9>"$HERE/build/.site-lock"
    flock -n 9 || { echo "deploy: another build or deploy is using build/site; try again when it ends" >&2; exit 4; }
    export AMIGAUX_SITE_LOCKED=1
fi

"$HERE/tools/build.sh" "${CHECK[@]}"
SITE="$HERE/build/site"

# The man pages are part of the site: a build without them (MAN_PKGS unset) still holds the
# frame they are made in.
if [[ -e "$SITE/man-frame.html" ]]; then
    echo "deploy: refusing: the man pages were not built (set MAN_PKGS, AMIX, AMIX_REF; see tools/build.sh)" >&2
    exit 3
fi

# Refuse to sync unless the build actually holds the site: with --delete an empty or
# half-built tree would wipe the docroot in one run.
for f in index.html site.css img/amiga-unix-boxcover.svg favicon.ico \
         font/oswald-600-latin.woff2 font/arimo-400-latin.woff2; do
    [[ -s "$SITE/$f" ]] || { echo "deploy: refusing: build/site/$f missing or empty" >&2; exit 3; }
done

DEST="${DEPLOY_DEST%/}"
echo "deploy: build/site/ -> $DEPLOY_HOST:$DEST/"
if [[ -n "$PREVIEW" ]]; then
    rsync -avz "${DRY[@]}" --delete-after --exclude='.*' "$SITE/" "$DEPLOY_HOST:$DEST/" 9>&-
else
# --delete-after: new files land before stale ones go, so a mid-run failure never leaves the
# docroot with files removed but their replacements absent.  These trees live only on the
# server and are excluded, so --delete never removes them (no --delete-excluded here):
#   /stats/   the visitor statistics, generated on the server
#   /sakuuu/  the demo-compo entry
#   /files/   the release downloads, no directory index
#   /video/   the demo clips
#   /preview/ the next release's site, deployed on its own
rsync -avz "${DRY[@]}" --delete-after --exclude='.*' --exclude='/stats/' --exclude='/sakuuu/' \
    --exclude='/files/' --exclude='/video/' --exclude='/preview/' \
    "$SITE/" "$DEPLOY_HOST:$DEST/" 9>&-
fi

if [[ ${#DRY[@]} -gt 0 ]]; then
    echo "deploy: dry run complete"
    exit 0
fi

echo "deploy: verifying $URL"
CODE="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 20 "$URL")"
[[ "$CODE" == "200" ]] || { echo "deploy: ERROR: $URL returned $CODE" >&2; exit 2; }
echo "deploy: OK ($URL -> 200)"
