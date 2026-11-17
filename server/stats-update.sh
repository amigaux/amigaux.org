#!/bin/bash
# Build the GoAccess dashboards for every site on this host, from the full log
# archive rather than just the live log.
#
# Two jobs, in order:
#   1. ARCHIVE every rotated log that is not archived yet. logrotate keeps only
#      14 days, so without this the history quietly expires -- including
#      2026-09-21, the Hacker News day, which is the busiest this site has had.
#      Files are named by the date of their FIRST log line, so re-archiving the
#      same day under a different rotated name (delaycompress renames .1 to
#      .2.gz the next day) cannot duplicate it.
#   2. REPORT: regenerate each site's HTML from archive + the live log. Rebuilding
#      from the whole archive each run, rather than accumulating into a database,
#      means the numbers are always exactly what the logs say -- no drift, no
#      double counting across a rotation, and a re-run after fixing anything is
#      just correct. At this volume it costs a couple of seconds.
#
# Runs as the deploy user: it is in the `adm` group, so it can read the logs,
# and it owns the docroot it writes into. No root.
#
#   ARCHIVE      where the rotated logs are kept (default /var/log-archive/apache2)
#   LOGS, OUT    the live logs and the dashboard directory
#   STATS_EXTRA  more sites on the same host, one dashboard each:
#                "prefix|output.html|title;..." (prefix: the access log's name
#                before -access.log, or "access" for the default vhost)
set -euo pipefail

ARCHIVE="${ARCHIVE:-/var/log-archive/apache2}"
LOGS="${LOGS:-/var/log/apache2}"
OUT="${OUT:-/var/www/amigaux.org/stats}"

mkdir -p "$ARCHIVE" "$OUT"

# ---------------------------------------------------------------- archive ---
shopt -s nullglob
for f in "$LOGS"/*access.log.1 "$LOGS"/*access.log.*.gz; do
    base=$(basename "$f")
    site=${base%%-access.log*}
    [ "$site" = "$base" ] && site=${base%%.log*}          # the default vhost's plain access.log
    d=$(zcat -f "$f" 2>/dev/null | head -1 | grep -oE '\[[0-9]{2}/[A-Za-z]{3}/[0-9]{4}' | tr -d '[' | head -1) || true
    [ -n "$d" ] || continue
    iso=$(date -d "${d//\// }" +%Y-%m-%d 2>/dev/null) || continue
    out="$ARCHIVE/${site}-${iso}.log.gz"
    [ -e "$out" ] || zcat -f "$f" | gzip -9 > "$out"
done
shopt -u nullglob

# ----------------------------------------------------------------- report ---
# --ignore-crawlers: these are visitor stats, and on a site that has been on
#   Hacker News the crawler share is large enough to drown the humans.
# --anonymize-ip: the dashboard never needs a full address to be useful, and
#   this keeps a password slip from turning into a disclosure of who visited.
# --enable-panel=REFERRERS: GoAccess's shipped config sets `ignore-panel
#   REFERRERS`, so the full referring-URL panel is off unless asked for. The
#   "Referring Sites" hostname panel is separate and always on.
# --geoip-database: DB-IP country lite. Free and downloadable without an
#   account, unlike MaxMind GeoLite2 which needs a licence key; refreshed
#   monthly by refresh-geoip.sh. CC BY 4.0, attributed on the stats index.
GEOIP="${GEOIP:-/usr/share/GeoIP/dbip-country-lite.mmdb}"
GA_OPTS=(--log-format=COMBINED --ignore-crawlers --anonymize-ip --no-progress
         --agent-list --real-os --http-method=yes --http-protocol=no
         --enable-panel=REFERRERS)
[ -r "$GEOIP" ] && GA_OPTS+=(--geoip-database="$GEOIP")

report() {                       # report <label> <output.html> <title> <prefix>
    local label="$1" out="$2" title="$3" prefix="$4"
    shopt -s nullglob
    local files=("$ARCHIVE/${prefix}"-*.log.gz "$LOGS/${prefix}"*access.log)
    shopt -u nullglob
    if [ ${#files[@]} -eq 0 ]; then
        echo "stats: $label -- no logs found, skipped" >&2
        return 0
    fi
    zcat -f "${files[@]}" \
        | goaccess - "${GA_OPTS[@]}" --html-report-title="$title" -o "$OUT/$out" 2>/dev/null
    echo "stats: $label -> $out ($(zcat -f "${files[@]}" | wc -l) lines)"
    INDEX+=" <li><a href=\"$out\">$title</a></li>"$'\n'
}

INDEX=
report "amigaux.org"     "amigaux.html"   "amigaux.org"                       "amigaux.org"
report "pkg.amigaux.org" "pkg.html"       "pkg.amigaux.org (package repo)"    "pkg.amigaux.org"
IFS=';' read -r -a EXTRA <<< "${STATS_EXTRA:-}"
for e in "${EXTRA[@]}"; do
    IFS='|' read -r prefix out title <<< "$e"
    [ -n "${prefix// /}" ] || continue
    report "$prefix" "$out" "$title" "$prefix"
done

# ------------------------------------------------------------------ index ---
cat > "$OUT/index.html" <<HTML
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>stats</title>
<style>
 body{background:#0b0b0b;color:#c9c9c9;font-family:system-ui,Helvetica,Arial,sans-serif;
      margin:0;padding:2.5rem 1.25rem;line-height:1.6}
 main{max-width:34rem;margin:0 auto}
 h1{font-size:1.1rem;letter-spacing:.14em;text-transform:uppercase;color:#fff;margin:0 0 1.5rem}
 ul{list-style:none;padding:0;margin:0}
 li{margin:.5rem 0}
 a{color:#fff;text-decoration:none;border-bottom:1px solid #4a4a4a;font-size:1.05rem}
 a:hover{border-bottom-color:#d62d2d}
 .n{color:#6a6a6a;font-size:.8rem;margin-top:2rem}
</style></head><body><main>
<h1>Visitor stats</h1>
<ul>
${INDEX}</ul>
<p class="n">Rebuilt every 15 minutes from the full log archive ($(date '+%Y-%m-%d %H:%M %Z')).
Crawlers excluded; addresses anonymised. History is kept in $ARCHIVE, which outlives
logrotate's 14 days. Country data from
<a href="https://db-ip.com">IP Geolocation by DB-IP</a> (CC BY 4.0).</p>
</main></body></html>
HTML
echo "stats: index -> $OUT/index.html"
