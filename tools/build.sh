#!/bin/bash
# Build the site into build/site/ (gitignored) and check it.
#
#   tools/build.sh                       MkDocs (strict), then tools/check-site.py
#   tools/build.sh --allow-placeholders  the same, a PLACEHOLDER marker only warns (on purpose)
#   tools/build.sh --preview             the unlinked preview for https://amigaux.org/preview/:
#                                        every page noindex with a banner, placeholders shown
#                                        as TBD, no sitemap; without MAN_PKGS /man/ is TBD
#   MKDOCS=/path/to/mkdocs               use that mkdocs (default: the one on PATH)
#
# The man pages under /man/ are built when MAN_PKGS is set:
#   MAN_PKGS="<dir> ..."   the release's package files (.pkg, .pkg.Z)
#   AMIX=<checkout>        an amix checkout holding the release's commit
#   AMIX_REF=<commit>      the release's pin (release/amix-<version>.lock, line "amix")
# Without MAN_PKGS the man frame stays in build/site/ and deploy.sh refuses the build.
#
# Needs: pip install -r requirements.txt; for the man pages a C compiler, make and zlib's
# headers (tools/build-mandoc.sh builds the pinned mandoc once).
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
MKDOCS="${MKDOCS:-mkdocs}"
cd "$HERE"
# One build at a time in this checkout: a second one would overwrite build/site under the first.
# deploy.sh holds this for the build and its sync, and says so in AMIGAUX_SITE_LOCKED.
if [[ -z "${AMIGAUX_SITE_LOCKED:-}" ]] && command -v flock >/dev/null; then
    mkdir -p build
    exec 9>build/.site-lock
    flock -n 9 || { echo "build: another build or deploy is using build/site; try again when it ends" >&2; exit 4; }
fi
PREVIEW_BASE=/preview/
unset AMIGAUX_PREVIEW AMIGAUX_BASE AMIGAUX_SITE_URL   # only --preview sets them
CHECK=("$@")
if [[ "${1:-}" == "--preview" ]]; then
    [[ $# -eq 1 ]] || { echo "build: --preview takes no other option" >&2; exit 1; }
    export AMIGAUX_PREVIEW=1 AMIGAUX_BASE="$PREVIEW_BASE" AMIGAUX_SITE_URL="https://amigaux.org$PREVIEW_BASE"
    CHECK=(--preview "$PREVIEW_BASE")
fi
"$MKDOCS" build --strict --clean --quiet
if [[ -n "${AMIGAUX_PREVIEW:-}" ]]; then
    rm -f build/site/sitemap.xml build/site/sitemap.xml.gz
fi
if [[ -n "${MAN_PKGS:-}" ]]; then
    : "${AMIX:?build: MAN_PKGS needs AMIX (an amix checkout)}" "${AMIX_REF:?build: MAN_PKGS needs AMIX_REF (the release commit)}"
    MANDOC="$(tools/build-mandoc.sh)"
    rm -rf build/man-src
    # shellcheck disable=SC2086  # MAN_PKGS is a list of directories
    python3 -I tools/man-collect.py --amix "$AMIX" --ref "$AMIX_REF" --out build/man-src $MAN_PKGS
    python3 -I tools/man-html.py --src build/man-src --site build/site --mandoc "$MANDOC"
    python3 -I tools/man-test.py --src build/man-src --site build/site
elif [[ -n "${AMIGAUX_PREVIEW:-}" ]]; then
    python3 -I tools/man-html.py --site build/site --empty
fi
python3 -I tools/check-site.py "${CHECK[@]}" build/site
