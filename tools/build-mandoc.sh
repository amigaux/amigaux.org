#!/bin/bash
# Build the pinned mandoc (tools/mandoc.pin) from source into build/tools/.
# Prints the path of the mandoc binary.  Needs a C compiler, make and zlib's headers.
#
#   tools/build-mandoc.sh        build once; later runs reuse the binary
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
PIN="$HERE/tools/mandoc.pin"
val() { awk -v k="$1" '$1 == k { print $2 }' "$PIN"; }
VER="$(val version)"; URL="$(val url)"; SUM="$(val sha256)"; SIZE="$(val size)"
OUT="$HERE/build/tools/mandoc-$VER"
BIN="$OUT/bin/mandoc"
if [[ -x "$BIN" && "$(cat "$OUT/.sha256" 2>/dev/null)" == "$SUM" ]]; then
    echo "$BIN"; exit 0
fi

WORK="$HERE/build/tools/mandoc-work"
rm -rf "$WORK" "$OUT"
mkdir -p "$WORK/dl" "$WORK/src" "$OUT/bin"
TAR="$WORK/dl/mandoc-$VER.tar.gz"
curl -fsSL "$URL" -o "$TAR" >&2
GOT="$(sha256sum "$TAR" | cut -d' ' -f1)"
LEN="$(stat -c %s "$TAR")"
if [[ "$GOT" != "$SUM" || "$LEN" != "$SIZE" ]]; then
    echo "build-mandoc: REFUSING: $URL is $GOT ($LEN bytes), the pin says $SUM ($SIZE bytes)" >&2
    exit 1
fi
tar -xzf "$TAR" -C "$WORK/src" --strip-components=1
(
    cd "$WORK/src"
    # configure.local: build the formatter only; nothing is installed system-wide.
    printf 'PREFIX="%s"\nSTATIC=\nUTF8_LOCALE=C.UTF-8\n' "$OUT" > configure.local
    ./configure >&2
    make -j"$(nproc)" mandoc >&2
)
install -m 0755 "$WORK/src/mandoc" "$BIN"
echo "$SUM" > "$OUT/.sha256"
rm -rf "$WORK"
echo "$BIN"
