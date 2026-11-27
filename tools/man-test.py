#!/usr/bin/env python3
"""Check the rendered /man/ against what readers rely on. tools/build.sh runs it after the man
pages are built; any failure stops the build.

usage: man-test.py --src <man-collect out> --site <built site>

It reads the built files, not man-html.py's data, so a mistake there shows here.
"""
import argparse
import json
import os
import re
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--site", required=True)
args = ap.parse_args()
MAN = os.path.join(args.site, "man")
errors = []


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8", errors="replace") as f:
        return f.read()


with open(os.path.join(args.src, "manifest.tsv"), encoding="utf-8") as f:
    rows = [l.rstrip("\n").split("\t") for l in f if l.strip()]
sections = sorted({r[1] for r in rows})

# Every section is named in plain language, on its own page and on the landing page.
landing = read(MAN, "index.html")
for s in sections:
    if f'<a href="{s}/">' not in landing:
        errors.append(f"/man/ does not list section {s}")
    head = re.search(r"<h2>(.*?)</h2>", read(MAN, s, "index.html"))
    if not head or not re.fullmatch(rf".+ \({re.escape(s.upper())}\)", head[1]):
        errors.append(f"/man/{s}/ has no plain name: {head[1] if head else 'no heading'}")

# Short addresses reach the page man(1) would show.
# With every package installed, a package's page wins its name: tar is GNU tar, ls GNU ls.
for name, want in (("tar", "1/tar"), ("ls", "1/ls"), ("cp", "1/cp"), ("printf", "1/printf"),
                   ("df", "1/df"), ("umount", "1m/mount"), ("zcat", "1/zcat"), ("ssh", "1/ssh"),
                   ("compress", "1/compress"), ("in.ftpd", "1m/ftpdfix"),
                   ("fopen", "3s/fopen"), ("strcpy", "3c/string"), ("stat", "1/stat"), ("man", "1/man"),
                   ("xterm", "1/xterm"), ("intro", "1/intro"), ("apkg", "1/apkg"), ("mount", "1m/mount")):
    path = os.path.join(MAN, name, "index.html")
    got = re.search(r'<a href="\.\./([^"]+)\.html">', read(path)) if os.path.exists(path) else None
    if not got or got[1] != want:
        errors.append(f"/man/{name}/ should go to {want}, goes to {got[1] if got else 'nothing'}")
for r in rows:
    if r[2].endswith("-original"):
        if os.path.exists(os.path.join(MAN, r[2])):
            errors.append(f"a kept original has a short address: /man/{r[2]}/")
    elif not os.path.exists(os.path.join(MAN, r[2], "index.html")):
        errors.append(f"no short address /man/{r[2]}/")

# The top of a page says where it is from and what else goes by its name. A package's page and
# the original it took the name of point at each other, and say which install brings the package.
tar = read(MAN, "1", "tar.html")
if ("Package: <code>gtar</code>" not in tar or "runs heirloom-tar: see <a href=\"../1/heirloom-tar.html\"" not in tar
        or 'href="../1/tar-original.html"' not in tar or "extra set" not in tar):
    errors.append("/man/1/tar.html lacks its package, its set or its notes about heirloom-tar and the original")
tar_o = read(MAN, "1", "tar-original.html")
if ("From the original Amiga UNIX 2.1 manual" not in tar_o or "see <a href=\"../1/heirloom-tar.html\"" not in tar_o
        or 'see <a href="../1/tar.html">' not in tar_o):
    errors.append("/man/1/tar-original.html lacks its stock line or its notes about heirloom-tar and GNU tar")
heir = read(MAN, "1", "heirloom-tar.html")
if ("Package: <code>heirtar</code>, added for amigaux" not in heir
        or '<a href="../1/tar-original.html">tar-original(1)</a>, the original page' not in heir):
    errors.append("/man/1/heirloom-tar.html lacks its package or its link to the original page")
pkgadd = read(MAN, "1m", "pkgadd.html")
if ("From the original Amiga UNIX 2.1 manual" not in pkgadd or 'href="../1m/pkgadd-apkgeng.html"' not in pkgadd
        or 'see <a href="../1m/pkgadd.html">' not in read(MAN, "1m", "pkgadd-apkgeng.html")):
    errors.append("/man/1m/pkgadd.html is not the original, or it and apkg's copy do not point at each other")
ls_o = read(MAN, "1", "ls-original.html")
if 'see <a href="../1/ls.html">' not in ls_o or 'href="../1/ls-original.html"' not in read(MAN, "1", "ls.html"):
    errors.append("/man/1/ls.html and /man/1/ls-original.html do not point at each other")
if 'class="head"' in read(MAN, "1", "dbclient.html"):
    errors.append("mandoc's header line is back on /man/1/dbclient.html")
if "../3b/printf.html" not in read(MAN, "1", "printf.html"):
    errors.append("/man/1/printf.html does not list printf(3B)")
if "<title>ls-original(1): list contents of directory" not in ls_o:
    errors.append("/man/1/ls-original.html has no description in its browser title")
sitemap = os.path.join(args.site, "sitemap.xml")
if os.path.exists(sitemap) and "/man/1/ls.html</loc>" not in read(sitemap):
    errors.append("sitemap.xml does not list the man pages")

# Every page can be reached from the A-Z, and the landing page offers the ways in.
az = read(MAN, "names", "index.html")
for r in rows:
    file = "index-page.html" if r[2] == "index" else f"{r[2]}.html"
    if f'href="../{r[1]}/{file}"' not in az:
        errors.append(f"/man/{r[1]}/{file} is not on the A-Z page")
    letter = r[2][0].lower() if r[2][0].isalpha() else "other"
    if f'href="../../{r[1]}/{file}"' not in read(MAN, "names", letter, "index.html"):
        errors.append(f"/man/{r[1]}/{file} is not on the A-Z page for {letter}")
for want, what in (("Common tasks", "the common tasks"), ('href="names/"', "the A-Z"), ('href="tar/"', "a short address"),
                   ('href="1/cp.html"', "copy files")):
    if want not in landing:
        errors.append(f"/man/ does not offer {what}")

# The search: the index knows every page and its words, and stays small. index.js and the parts
# loaded at first use stay within the budget together; each part on its own too.
BUDGET = 160_000
index_js = read(MAN, "index.js")
m = re.match(r"MANSECT=(\{.*\});\nMANORDER=(\[.*\]);\nMANPARTS=(\[.*\]);\nMANADD\((\".*\")\);\n\Z", index_js, re.S)
if not m:
    errors.append("/man/index.js is not what theme/man.js expects")
else:
    order, part_list = json.loads(m[2]), json.loads(m[3])
    lines = [l.split("\t") for l in json.loads(m[4]).split("\n")]
    first = len(index_js.encode())
    for part in part_list:
        data = read(MAN, part["f"])
        pm = re.fullmatch(r"MANADD\((\".*\")\);\n", data, re.S)
        if not pm:
            errors.append(f"/man/{part['f']} is not what theme/man.js expects")
            continue
        lines += [l.split("\t") for l in json.loads(pm[1]).split("\n")]
        size = len(data.encode())
        if size > BUDGET:
            errors.append(f"/man/{part['f']} has grown to {size} bytes")
        if not part["later"]:
            first += size
    if first > BUDGET:
        errors.append(f"the search loads {first} bytes at first use")
    stray = {f for f in os.listdir(MAN) if f.startswith("index") and f.endswith(".js")} - {"index.js"} \
        - {part["f"] for part in part_list}
    if stray:
        errors.append(f"/man/ has index files no part names: {sorted(stray)}")
    if any(len(l) != 8 for l in lines):
        errors.append("the search index has a line without its eight fields")
    known = {(l[1], l[0]) for l in lines}
    for r in rows:
        if (r[1], r[2]) not in known:
            errors.append(f"the search index lacks {r[1]}/{r[2]}")
    missing = set(sections) - set(json.loads(m[1]))
    if missing:
        errors.append(f"the search index lacks section names: {sorted(missing)}")
    if set(sections) - set(order):
        errors.append(f"MANORDER lacks sections: {sorted(set(sections) - set(order))}")
    cp = [l for l in lines if l[:2] == ["cp", "1"]]
    if not cp or "copy" not in cp[0][5]:
        errors.append("the search index has no task words for cp")
    if not any(l[7] == "../docs/sound/" for l in lines):
        errors.append("the search index lacks the site's Sound page")
if os.path.getsize(os.path.join(args.site, "man.js")) > 8000:
    errors.append("man.js has grown past 8 KB")
if '<div id="mansearch"' not in read(MAN, "1", "ls.html") or '<div id="mansearch"' not in landing:
    errors.append("a page has no place for the search box")

# The site's pages link in.
services = read(args.site, "docs", "services", "index.html")
if '../../man/1m/ntpsync.html"><code>ntpsync(1M)</code></a>' not in services:
    errors.append("/docs/services/ does not link ntpsync(1M)")

# Every page says what it is, in its section's list; preformatted pages have real headings.
for s_ in sections:
    for m in re.finditer(r'<a href="([^"]+)\.html"><code>[^<]*</code></a></td><td>(.*?)</td>', read(MAN, s_, "index.html")):
        if not m[2].strip():
            errors.append(f"/man/{s_}/{m[1]}.html has no description")
ls = ls_o
if '<h1 class="Sh" id="DESCRIPTION">DESCRIPTION</h1>' not in ls:
    errors.append("/man/1/ls-original.html has no heading for DESCRIPTION")
for page_, has in (("1/ksh", True), ("1/xls", False)):
    if ('class="man-jump"' in read(MAN, *f"{page_}.html".split("/"))) != has:
        errors.append(f"/man/{page_}.html: jump links should {'be there' if has else 'not be there'}")
headless = [f"{r[1]}/{r[2]}" for r in rows if r[0] == "cat" and r[2] != "xls" and '<h1 class="Sh"' not in
            read(MAN, r[1], ("index-page" if r[2] == "index" else r[2]) + ".html")]
if len(headless) > 25:
    errors.append(f"{len(headless)} preformatted pages have no headings: {headless[:8]}")

# Justified text flows; tables stay exactly as they are.
if not re.search(r'<p class="[^"]*">[^\n]*lists the contents of the directory;', re.sub(r"</?[bi]>", "", ls)):
    errors.append("/man/1/ls-original.html: its text does not flow")
ascii_ = re.sub(r"</?[bi]>", "", read(MAN, "5", "ascii.html"))
at = ascii_.find("|000 nul |001 soh")
if at < 0 or ascii_.rfind("<pre", 0, at) < ascii_.rfind("</pre", 0, at):
    errors.append("/man/5/ascii.html: its table is no longer preformatted")
for page_, must_stay in (("4/mailsurr", "'.+!.+'   'attmail!.+'    'Deny'"),
                         ("1m/crash", "gdp [-e] [-f] [-w file]")):
    if not re.search(r"<pre[^>]*>[^<]*" + re.escape(must_stay), re.sub(r'</?[bi]>|</?a\b[^>]*>', "", read(MAN, *f"{page_}.html".split("/")))):
        errors.append(f"/man/{page_}.html: {must_stay!r} should stay as it is")

# A dash at a line end stays a word: on a NAME line it must not read like an option.
for r in rows:
    if r[0] != "cat":
        continue
    text = read(MAN, r[1], ("index-page" if r[2] == "index" else r[2]) + ".html")
    m = re.search(r'id="NAME">NAME</h1>\s*<p[^>]*>(.*?)</p>', text, re.S)
    if m and re.search(r"\s-[a-zA-Z]{3,}", re.sub(r"<[^>]+>", "", m[1])) and not re.search(r"\s-\s", re.sub(r"<[^>]+>", "", m[1])):
        errors.append(f"/man/{r[1]}/{r[2]}.html: the dash of its NAME line has joined the next word")
for page_, want in (("2/signal", "sigpause - simplified"), ("3c/memory", "memset - memory"), ("3b/setjmp", "siglongjmp - non-local")):
    if want not in re.sub(r"<[^>]+>", "", read(MAN, *f"{page_}.html".split("/"))):
        errors.append(f"/man/{page_}.html: {want!r} is not on the page")

# A list entry the old page break cut in two is whole again; a marked plain word is not code.
for page_, want in (("1/cscope", "version number of cscope."), ("1/ed", "matches the concatenation of the strings"),
                    ("1m/mount", "systems in the /etc/vfstab format.")):
    if want not in re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", read(MAN, *f"{page_}.html".split("/")))):
        errors.append(f"/man/{page_}.html: {want!r} is still split")
ed = read(MAN, "1", "ed.html")
if '<i class="c">zero</i>' in ed or "<i>zero</i>" not in ed:
    errors.append("/man/1/ed.html: the word zero should be plain emphasis, not code")
if not re.search(r'<i class="c n">[^<]*\\', ed):
    errors.append("/man/1/ed.html: a regular expression can wrap after its backslash")

# Overstruck text survives: a ruled table's header, and an underlined comparison sign in running text.
if "Used" not in re.sub(r"</?[bi]>", "", read(MAN, "1", "get.html")):
    errors.append("/man/1/get.html: the header of its table has gone under the rule")
if not re.search(r"\(1 <u>&lt;</u> <i[^>]*>n</i> <u>&lt;</u> 365\)", read(MAN, "5", "environ.html")):
    errors.append("/man/5/environ.html: the underlined < has lost its underline")

# Cross references: the right page, or plain text where the same name is something else.
for page_, name, sect, target in (("1x/pgmtopbm", "pbm", "5", "../5l/pbm.html"),
                                  ("1/dbclient", "dropbear", "8", "../8/dropbear.html"),
                                  ("3e/elf_begin", "elf_end", "3E", "../3e/elf_end.html"),
                                  ("3/ieee_handler", "signal", "3F", None),
                                  ("1a/fractal", "screen", "1A", None)):
    text = re.sub(r"</?[bi]>", "", read(MAN, *f"{page_}.html".split("/")))
    ref = rf"{re.escape(name)}\({sect}\)"
    found = re.findall(rf'<a href="([^"]+)">{ref}</a>', text)
    if not re.search(ref, text):
        errors.append(f"/man/{page_} no longer mentions {name}({sect}): pick another test")
    elif target is None and found:
        errors.append(f"/man/{page_}: {name}({sect}) should stay text, links to {found}")
    elif target is not None and target not in found:
        errors.append(f"/man/{page_}: {name}({sect}) should link to {target}, found {found}")

for e in errors:
    print("man-test:", e, file=sys.stderr)
if errors:
    sys.exit(1)
print(f"man-test: {len(rows)} pages in {len(sections)} sections OK")
