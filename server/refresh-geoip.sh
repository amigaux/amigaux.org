#!/bin/bash
# Refresh the country database. DB-IP publish a new free build each month at a
# dated URL, so this tries this month and falls back to last month (early in
# the month the new one may not be up yet). Writes only on a successful,
# non-empty download, so a failed fetch leaves the working database in place.
set -euo pipefail
DEST="${DEST:-/usr/share/GeoIP/dbip-country-lite.mmdb}"
TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
for m in "$(date +%Y-%m)" "$(date -d '1 month ago' +%Y-%m)"; do
    url="https://download.db-ip.com/free/dbip-country-lite-${m}.mmdb.gz"
    if curl -fsS -L --max-time 180 "$url" | gunzip > "$TMP" 2>/dev/null && [ -s "$TMP" ]; then
        install -m 644 "$TMP" "$DEST"
        echo "refresh-geoip: updated $DEST from $m ($(stat -c%s "$DEST") bytes)"
        exit 0
    fi
done
echo "refresh-geoip: no new database available; keeping the existing one" >&2
exit 0
