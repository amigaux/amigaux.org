#!/usr/bin/env python3
"""Collect the man pages of a release's packages, for the site's /man/.

usage: man-collect.py --amix <amix checkout> --ref <release commit> --out <dir> <pkg dir> ...

Only the package files the repository's catalog (beside <pkg dir>) lists as current are read,
when there is one. The packages are read with amix's own datastream reader (userland/pkgtools/tools/repo/
gen-catalog.py), taken from the amix checkout at --ref: the release's pin. Each package's
pkgmap names its files; the man pages among them are unpacked from its payload. Nothing is
installed and nothing outside --out is written.

<out>/troff/<section>/<name>   troff source (mandoc renders it)
<out>/cat/<section>/<name>     preformatted pages (the stock /usr/share/catman), shown as text
<out>/manifest.tsv             kind, section, name, package, installed path
<out>/missing.tsv              pages a pkgmap names that the payload does not hold
<out>/replaces.tsv             replaced stock programs, from the packages' man/replaces.d tables:
                               binary path, section, page (what man(1) shows for that program)
A .Z page is decompressed. When two pages share a section and name, the added software's
page takes the name and the stock one is kept as <name>-original (man -a shows both on the
box), except apkg's own copies under /usr/apkg, which go aside as <name>-apkgeng; among stock pages the troff source wins over the preformatted one; any other clash is
reported, and the later page kept.
"""
import argparse
import importlib.util
import os
import re
import subprocess
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--amix", required=True)
ap.add_argument("--ref", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("pkgdirs", nargs="+")
args = ap.parse_args()

READER = "userland/pkgtools/tools/repo/gen-catalog.py"
src = subprocess.run(["git", "-C", args.amix, "show", f"{args.ref}:{READER}"],
                     check=True, stdout=subprocess.PIPE).stdout
os.makedirs(args.out, exist_ok=True)
modpath = os.path.join(args.out, ".gen_catalog.py")
with open(modpath, "wb") as f:
    f.write(src)
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("gen_catalog", modpath)
gc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gc)

# (pattern, kind, stock?): group 1 is the section, group 2 the name.
PATTERNS = [
    (re.compile(r"^/usr/share/catman/([^/]+)/([^/]+?)(?:\.Z)?$"), "cat", True),
    (re.compile(r"^/usr/share/man/([^/]+)/([^/]+?)(?:\.Z)?$"), "troff", True),
    (re.compile(r"^/usr/apkg/man/man([^/]+)/([^/]+?)\.[^./]+$"), "troff", False),  # see ASIDE
    (re.compile(r"^/opt/amix/man/([^/]+)/([^/]+)$"), "troff", False),
    (re.compile(r"/man/man([^/]+)/([^/]+?)\.[^./]+$"), "troff", False),
]


def classify(path):
    for rx, kind, stock in PATTERNS:
        m = rx.search(path)
        if m:
            return kind, m.group(1).lower(), m.group(2), stock
    return None


def unz(data):
    if data[:2] != b"\x1f\x9d":
        return data
    return subprocess.run(["gzip", "-dc"], input=data, check=True, stdout=subprocess.PIPE).stdout


def current_files(d):
    """The package files a repository's catalog (beside the pkgs directory) lists as current, as
    paths under d; None when there is no catalog. Older versions the tree keeps are left out."""
    cat = os.path.join(os.path.dirname(os.path.abspath(d)), "catalog")
    if not os.path.exists(cat):
        return None
    files = set()
    with open(cat, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#kpkg "):
                files.add(re.search(r"\bfile=(\S+)", line).group(1))
            elif not line.startswith("#") and line.count("|") >= 8:
                files.add(line.split("|")[3])
    return files


def packages(dirs):
    for d in dirs:
        current = current_files(d)
        for root, _, files in os.walk(d):
            for f in sorted(files):
                rel = os.path.relpath(os.path.join(root, f), d)
                if f.endswith((".pkg", ".pkg.Z")) and (current is None or rel in current):
                    yield os.path.join(root, f)


chosen = {}     # (section, name) -> (kind, stock, pkginst, path, data)
# A stock page whose name a package's page takes is kept beside it as <name>-original, as
# man -a on the box shows both: which one man(1) shows depends on what is installed.
ORIGINAL = "-original"
# apkg's own copies of the package tools live in /usr/apkg, off PATH and outside man(1)'s trees:
# `pkgadd` at the shell runs the original. Their pages keep a name of their own, <name>-apkgeng,
# when a stock page has the name.
ASIDE = "/usr/apkg/man/"


def aside_name(name, pkginst):
    return f"{name}-{pkginst.lower()}"


def keep_original(sect, name, entry):
    key = (sect, name + ORIGINAL)
    have = chosen.get(key)
    if have and have[0] == "troff" and entry[0] == "cat":       # stock: troff over preformatted
        return
    chosen[key] = entry


missing, clashes, npkg = [], [], 0
replaces = []   # (binary path, section, page)
for pkgfile in packages(args.pkgdirs):
    buf = gc.decompress_z(pkgfile) if pkgfile.endswith(".Z") else open(pkgfile, "rb").read()
    pkginst, params, pkgmap = gc.parse_datastream(buf)
    npkg += 1
    if not pkgmap:
        continue
    basedir = params.get("BASEDIR", "/")
    want, tables = {}, []
    for ftype, _cls, path in gc.pkgmap_objects(pkgmap, basedir):
        if ftype not in ("f", "v", "e"):
            continue
        if "/man/replaces.d/" in path:
            tables.append(path)
            continue
        c = classify(path)
        if c and not path.endswith(("/whatis", "/base_whatis")) and "/whatis.d/" not in path:
            want[path] = c
    if not want and not tables:
        continue
    found = gc.payload_files(buf, list(want) + tables, basedir)
    for path in tables:
        if path not in found:
            missing.append((pkginst, path))
            continue
        for line in unz(found[path]).decode("utf-8", "replace").split("\n"):
            f = line.split()
            if len(f) == 3 and not line.startswith("#"):
                replaces.append((f[0], f[1].lower(), f[2]))
    for path, (kind, sect, name, stock) in sorted(want.items()):
        if path not in found:
            missing.append((pkginst, path))
            continue
        key = (sect, name)
        entry = (kind, stock, pkginst, path, None)
        if stock and name.endswith(ORIGINAL):
            sys.exit(f"man-collect: a stock page is named like a kept original: {sect}/{name}")
        if key in chosen and ((path.startswith(ASIDE) and chosen[key][1])
                              or (stock and chosen[key][3].startswith(ASIDE))):
            if path.startswith(ASIDE):        # the stock page keeps its name
                chosen[(sect, aside_name(name, pkginst))] = entry[:4] + (unz(found[path]),)
                continue
            old = chosen[key]
            chosen[(sect, aside_name(name, old[2]))] = old
        elif key in chosen:
            old = chosen[key]
            if old[1] and not stock:          # ours takes the name, the stock page moves aside
                keep_original(sect, name, old)
            elif stock and not old[1]:        # ours keeps the name, the stock page goes aside
                keep_original(sect, name, entry[:4] + (unz(found[path]),))
                continue
            elif stock and old[1] and old[0] != kind:   # stock: troff over preformatted
                if kind == "cat":
                    continue
            else:
                clashes.append((sect, name, old[2], pkginst))
        chosen[key] = (kind, stock, pkginst, path, unz(found[path]))

with open(os.path.join(args.out, "manifest.tsv"), "w") as man:
    for (sect, name), (kind, stock, pkginst, path, data) in sorted(chosen.items()):
        d = os.path.join(args.out, kind, sect)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, name), "wb") as f:
            f.write(data)
        man.write(f"{kind}\t{sect}\t{name}\t{pkginst}\t{path}\n")
with open(os.path.join(args.out, "missing.tsv"), "w") as f:
    for pkginst, path in missing:
        f.write(f"{pkginst}\t{path}\n")
with open(os.path.join(args.out, "replaces.tsv"), "w") as f:
    for row in sorted(replaces):
        f.write("\t".join(row) + "\n")
os.remove(modpath)

kinds = {}
for kind, *_ in chosen.values():
    kinds[kind] = kinds.get(kind, 0) + 1
print(f"man-collect: {npkg} packages, {len(chosen)} pages "
      + ", ".join(f"{n} {k}" for k, n in sorted(kinds.items()))
      + f"; {len(missing)} named but not in the payload; {len(clashes)} same-name clashes")
for sect, name, a, b in clashes[:20]:
    print(f"man-collect: clash {name}({sect}): {a} and {b}; kept {b}", file=sys.stderr)
