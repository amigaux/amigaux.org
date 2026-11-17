#!/usr/bin/env python3
"""Render the collected man pages (tools/man-collect.py) into the built site's /man/.

usage: man-html.py --src <man-collect out> --site <built site> (--mandoc <path> | --no-troff)
       man-html.py --site <built site> --empty

  troff pages     mandoc -T html -O fragment; a page that is only a .so shows its target
  preformatted    the original pages' nroff output: bold and underline overstrikes become <b>
                  and <i>, headings become headings, and text nroff justified flows again (the
                  words checked unchanged, word by word); anything that may be a table stays as it is, in a <pre>
A reference name(section) links to its page when the site has one, and stays text otherwise;
<src>/refs-widened.tsv and refs-unlinked.tsv say what the same-number rule did and what stayed text.
Each page goes into the frame MkDocs built (man-frame.html, then removed) at
/man/<section>/<name>.html (a page named index: index-page.html, as index.html is the
section's list). /man/<section>/ lists a section's pages with their descriptions, /man/names/ all
of them A-Z. The <!--MANSECTIONS--> marker of /man/ becomes the common tasks (tools/man-tasks.tsv),
the A-Z and the sections by their plain names (tools/man-sections.tsv). /man/<name>/ is a short address for every name a page goes by: a small
file sending the reader to the page man(1) would show (section order below, a package's
replacement of a stock program first). /man/index.js is what the search box (theme/man.js) reads.
--no-troff skips the troff pages (a test without mandoc); a deploy always passes --mandoc.
--empty (the preview build without the release's packages) only removes the frame and marks
/man/ as TBD.
"""
import argparse
import collections
import gzip
import html
import json
import os
import re
import subprocess
import sys
import types

ap = argparse.ArgumentParser()
ap.add_argument("--src")
ap.add_argument("--site", required=True)
g = ap.add_mutually_exclusive_group(required=True)
g.add_argument("--mandoc")
g.add_argument("--no-troff", action="store_true")
g.add_argument("--empty", action="store_true")
args = ap.parse_args()
if not args.empty and not args.src:
    ap.error("--src is required unless --empty")

TOOLS = os.path.dirname(os.path.abspath(__file__))
FRAME = os.path.join(args.site, "man-frame.html")
with open(FRAME, encoding="utf-8") as f:
    frame = f.read()
for marker in ("<!--MANTITLE-->", "<!--MANHEAD-->", "<!--MANPAGE-->"):
    if marker not in frame:
        sys.exit(f"man-html: {FRAME} lacks {marker}")
MAN = os.path.join(args.site, "man")
SITE_BASE = re.search(r'href="([^"]*)man\.css"', frame)[1]     # "/", or "/preview/" in the preview

if args.empty:
    idx = os.path.join(MAN, "index.html")
    with open(idx, encoding="utf-8") as f:
        landing = f.read()
    if "<!--MANSECTIONS-->" not in landing:
        sys.exit(f"man-html: {idx} lacks <!--MANSECTIONS-->")
    note = '<p><span class="ph">TBD: the pages, built from the release\'s packages</span></p>'
    with open(idx, "w", encoding="utf-8") as f:
        f.write(landing.replace("<!--MANSECTIONS-->", note))
    os.remove(FRAME)
    print("man-html: no man pages (--empty); /man/ marked TBD")
    sys.exit(0)


def page(title, body, head=""):
    return (frame.replace("<!--MANTITLE-->", html.escape(title)).replace("<!--MANHEAD-->", head)
            .replace("<!--MANPAGE-->", body))


# ---- preformatted pages ------------------------------------------------------------------

def overstrike(raw):
    """nroff terminal output -> HTML: c\\bc is bold, _\\bc and c\\b_ underlined (shown as <i>), the
    second being how a ruled table's header row comes out; +\\bo is a bullet."""
    out = []
    for line in raw.split("\n"):
        cells = []                       # (char, attr)
        i = 0
        while i < len(line):
            c = line[i]
            if c == "\b" and cells:
                nxt = line[i + 1] if i + 1 < len(line) else ""
                prev, attr = cells[-1]
                if nxt:
                    if prev == "_" and nxt != "_":
                        cells[-1] = (nxt, "i")
                    elif nxt == "_" and prev != "_":
                        cells[-1] = (prev, "i")
                    elif {prev, nxt} == {"+", "o"}:
                        cells[-1] = ("\u2022", attr)
                    elif prev == nxt:
                        cells[-1] = (nxt, "b" if attr != "i" else "i")
                    else:
                        cells[-1] = (nxt, attr)
                    i += 2
                    continue
            cells.append((c, ""))
            i += 1
        s, cur = [], ""
        for c, a in cells:
            if a != cur:
                if cur:
                    s.append(f"</{cur}>")
                if a:
                    s.append(f"<{a}>")
                cur = a
            s.append(html.escape(c, quote=False))
        if cur:
            s.append(f"</{cur}>")
        out.append("".join(s))
    return "\n".join(out)


def plain(raw):
    return re.sub(r".\x08", "", re.sub(r"([^_\x08])\x08_", r"\1", raw))


def depaginate(raw):
    """Drop nroff's page furniture: the running header (the page's first line, repeated on
    every page), the numbered page footers, and the blank padding between pages."""
    shown = overstrike(raw).split("\n")
    text = plain(raw).split("\n")
    nonblank = [t for t in text if t.strip()]
    header = nonblank[0] if len(nonblank) > 1 else None      # a one-line page is all text
    feet = {}
    for t in text:
        m = re.match(r"^(.*\S)\s+(\d+)\s*$", t)
        if m:
            feet.setdefault(re.sub(r"\s+", " ", m.group(1).strip()), []).append(int(m.group(2)))
    footers = {k for k, nums in feet.items() if nums == list(range(1, len(nums) + 1))
               and (len(nums) > 1 or "Last change" in k)}
    keep = []
    for t, h in zip(text, shown):
        if t == header:
            continue
        m = re.match(r"^(.*\S)\s+(\d+)\s*$", t)
        if m and re.sub(r"\s+", " ", m.group(1).strip()) in footers:
            continue
        keep.append(h)
    out, blank = [], 0
    for h in keep:
        if not h.strip():
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        out.append(h)
    return "\n".join(out).strip("\n")


# ---- names and descriptions -----------------------------------------------------------------

REFNAME = r"[A-Za-z_][\w.+-]*"
REFSECT = r"\d[A-Za-z]*"


def name_line_cat(raw):
    lines = plain(raw).split("\n")
    nonblank = [l.strip() for l in lines if l.strip()]
    if len(nonblank) == 1:
        return nonblank[0]
    # NAME, or as the widget pages head it, WIDGET CLASS NAME.
    for head in (r"NAME", r"(?:[A-Z]+ )+NAME"):
        for i, l in enumerate(lines):
            if re.fullmatch(head, l.strip()):
                desc = ""
                for m in lines[i + 1:]:
                    if not m.strip():
                        if desc:
                            break
                        continue
                    m = m.strip()
                    if re.search(r"[a-z]-$", desc) and m[0].islower():
                        desc = desc[:-1] + m        # a word nroff hyphenated at the line end
                    else:
                        desc = f"{desc} {m}" if desc else m
                return desc
    return ""


def name_line_troff(raw):
    m = re.search(r"^\.S[Hh]\s+\"?NAME\"?\s*\n(.*?)(?=^\.S[Hh]|\Z)", raw, re.M | re.S)
    if m:
        lines = [re.sub(r"^\.(?:B|I|BR|IR|RB|RI)\s+", "", l) for l in m.group(1).split("\n")]
        text = " ".join(l.replace('"', "") for l in lines if l and not l.startswith((".", "'")))
    else:       # no NAME section: the page's first line of text
        text = next((l for l in raw.split("\n") if l.strip() and not l.startswith((".", "'"))), "")
    text = re.sub(r"\\f[BIRP]|\\f\(..|\\&|\\\(em", "", text)
    return text.replace("\\-", "-").replace("\\e", "\\").strip()


def split_name(line):
    """A NAME line as (the names it gives, the description). Notes such as the (generic) of
    "mount, umount (generic) - ..." are not names."""
    m = re.match(r"(.*?)(?:^|\s+)-+\s+(.*)", line)
    if not m:
        return [], line.strip()
    names = [n.strip() for n in re.sub(r"\([^)]*\)", "", m.group(1)).split(",")]
    return [n for n in names if re.fullmatch(REFNAME, n)], m.group(2).lstrip("- ").strip()


def pagefile(name):
    return "index-page.html" if name == "index" else f"{name}.html"


def troff_source(raw):
    """The text mandoc renders. A page that is only a .so is its target: mandoc refuses an
    absolute .so. In a script that is also a man page (h2ph), nroff skips the script with
    .ig and a diversion and mandoc prints it, so such a page starts at its .TH."""
    for _ in range(5):
        lines = [l for l in raw.split("\n") if l.strip() and not l.startswith('.\\"')]
        m = re.fullmatch(r"\.so\s+(/\S+)\s*", lines[0]) if len(lines) == 1 else None
        if not m:
            break
        if m.group(1) not in troff_paths:
            sys.exit(f"man-html: .so names a page not collected: {m.group(1)}")
        with open(troff_paths[m.group(1)], "rb") as f:
            raw = f.read().decode("latin-1")
    th = re.search(r"^\.TH\b", raw, re.M)
    if th and re.search(r"^'ig00", raw[:th.start()], re.M):
        return raw[th.start():]
    return raw


# ---- the pages, and which page a name means ---------------------------------------------------

def read_table(name):
    with open(os.path.join(TOOLS, name), encoding="utf-8") as f:
        return [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]


groups, section_names = {}, {}      # group -> [section], section -> plain name
for group, code, plain_name in read_table("man-sections.tsv"):
    groups.setdefault(group, []).append(code)
    section_names[code] = plain_name


def section_label(sect):
    return f"{section_names[sect]} ({sect.upper()})"


with open(os.path.join(args.src, "manifest.tsv"), encoding="utf-8") as mf:
    rows = [l.rstrip("\n").split("\t") for l in mf if l.strip()]
troff_paths = {path: os.path.join(args.src, kind, sect, name)
               for kind, sect, name, _, path in rows if kind == "troff"}
refused = {(r[0], r[1]) for r in read_table("man-refs-refused.tsv")}
descriptions = {(r[0], r[1]): r[2] for r in read_table("man-descriptions.tsv")}

man_pages = []
by_key, by_file, by_other = {}, {}, {}      # (section, name), name, other name on a NAME line
for kind, sect, name, pkg, path in rows:
    with open(os.path.join(args.src, kind, sect, name), "rb") as f:
        raw = f.read().decode("latin-1")
    if kind == "troff":
        raw = troff_source(raw)
    line = name_line_cat(raw) if kind == "cat" else name_line_troff(raw)
    others, desc = split_name(re.sub(r"\s+", " ", line))
    desc = desc or descriptions.get((sect, name), "")
    p = types.SimpleNamespace(kind=kind, sect=sect, name=name, pkg=pkg, path=path, raw=raw,
                              desc=desc, others=[n for n in others if n != name])
    man_pages.append(p)
    by_key[(sect, name)] = p
    by_file.setdefault(name, []).append(p)
    for n in p.others:
        by_other.setdefault(n, []).append(p)

unnamed = sorted({sect for sect, _ in by_key} - set(section_names))
if unnamed:
    sys.exit(f"man-html: no name in tools/man-sections.tsv for section(s) {', '.join(unnamed)}")

# man(1) tries these first, in this order, then any other. Among the others, a section's
# standard pages come before its BSD and XENIX versions.
MAN_ORDER = ["1", "1m", "8", "2", "3", "4", "5", "6", "7"]
COMPAT = {"1b", "2z", "3b", "4b", "4z"}


def section_key(sect):
    if sect in MAN_ORDER:
        return (MAN_ORDER.index(sect), 0, False, sect)
    return (len(MAN_ORDER), int(sect[0]), sect in COMPAT, sect)


replaced_by = {}        # a program's name -> the page shown for it, from the packages' replaces.d
replaces_tsv = os.path.join(args.src, "replaces.tsv")
if os.path.exists(replaces_tsv):
    with open(replaces_tsv, encoding="utf-8") as f:
        for line in f:
            binary, sect, name = line.rstrip("\n").split("\t")
            if (sect, name) not in by_key:
                sys.exit(f"man-html: replaces.d names a page not collected: {sect}/{name}")
            replaced_by[os.path.basename(binary)] = by_key[(sect, name)]


# A stock page whose name a package's page took is kept as <name>-original: on the box, man(1)
# shows the package's page once the package is installed, the original before. Each pair says
# which set brings the package, from tools/man-package-sets.tsv.
ORIGINAL = "-original"
package_sets = {r[0]: r[1] for r in read_table("man-package-sets.tsv")}
COMMAND_SECTS = {"1", "1m", "8"}


def is_stock(p):
    return p.path.startswith("/usr/share/")


# apkg's own copies of the package tools, off PATH: kept as <name>-apkgeng beside the original.
APKG_MAN = "/usr/apkg/man/"


def aside_of(p):
    """apkg's own page beside a stock one, or None."""
    return next((q for q in by_file.get(p.name + "-apkgeng", []) if q.sect == p.sect), None)


def aside_base(p):
    """The original a page of apkg's own was set aside from, or None."""
    if not (p.path.startswith(APKG_MAN) and p.name.endswith("-apkgeng")):
        return None
    return by_key.get((p.sect, p.name[:-len("-apkgeng")]))


def original_of(p):
    """The kept original of a package's page, or None."""
    return None if p.name.endswith(ORIGINAL) else by_key.get((p.sect, p.name + ORIGINAL))


def package_of(p):
    """The package's page that took a kept original's name, or None."""
    return by_key.get((p.sect, p.name[:-len(ORIGINAL)])) if p.name.endswith(ORIGINAL) else None


unset = sorted({q.pkg for q in man_pages if original_of(q)} - set(package_sets))
if unset:
    sys.exit(f"man-html: no set in tools/man-package-sets.tsv for package(s) {', '.join(unset)}")


def short_target(name):
    """The page /man/<name>/ goes to: the page man(1) shows with every package installed. A
    replaced stock program's page is the replacement's, unless a package's page has the name."""
    added = [p for p in by_file.get(name, []) if p.sect in COMMAND_SECTS and not is_stock(p)]
    if name in replaced_by and not added:
        return replaced_by[name]
    return min(by_file.get(name, []) + by_other.get(name, []),
               key=lambda p: (section_key(p.sect), p.name != name, p.name))


short_names = sorted((set(by_file) | set(by_other)) - {n for n in by_file if n.endswith(ORIGINAL)})
RESERVED = {"names", "index.html", "index.js"} | set(section_names)
taken = sorted(RESERVED & set(short_names))
if taken:
    sys.exit(f"man-html: a man page takes a name /man/ needs for itself: {', '.join(taken)}")


# ---- cross references -------------------------------------------------------------------------

# A name may change font part way: <i>elf</i><b>_</b><i>end</i>(3E) is elf_end(3E).
REF = re.compile(r"(?P<tag><(?!/?[bi]>)[^>]*>)"
                 r"|(?<![\w.+-])(?<!</b>)(?<!</i>)"
                 rf"(?P<name>(?:<[bi]>[\w.+-]+</[bi]>|[\w.+-])+)\((?P<sect>{REFSECT})\)")
FONT = re.compile(r"</?[bi]>")
# The end of a name nroff broke over a line: elf_ / end(3E) is elf_end(3E), not end(3E).
LINE_BROKEN = re.compile(r"[_-](?:</[bi]>)?\s*\n\s*(?:<[bi]>)?$")
linked = 0
widened, unlinked = {}, {}      # (name, section, page) and (name, section) -> pages using it


def ref_target(name, sect, here):
    """The page a reference name(sect) from section `here` means: the exact page, a page giving
    that name on its NAME line in that section, or the same name under the same main number
    (pbm(5) is pbm(5L)) unless tools/man-refs-refused.tsv says it is something else."""
    if (sect, name) in by_key:
        return by_key[(sect, name)]
    same = [p for p in by_other.get(name, ()) if p.sect == sect]
    if same:
        return same[0]
    if (name, sect) in refused:
        return None
    near = [p for p in by_file.get(name, []) + by_other.get(name, []) if p.sect[0] == sect[0]]
    if not near:
        return None
    best = min(near, key=lambda p: (p.sect != here, section_key(p.sect), p.name != name, p.name))
    widened.setdefault((name, sect, f"{best.sect}/{best.name}"), []).append(here)
    return best


def link_refs(body, here):
    """Link name(section) to its page, when the site has one. Not inside another link, not
    in mandoc's header and footer lines, and not a page's mention of itself."""
    skip = None

    def sub(m):
        global linked
        nonlocal skip
        if m["tag"]:
            t = m["tag"]
            if skip:
                if t.startswith(skip):
                    skip = None
            elif t.startswith("<a "):
                skip = "</a>"
            elif t.startswith(('<table class="head"', '<table class="foot"')):
                skip = "</table>"
            return t
        name, sect = FONT.sub("", m["name"]), m["sect"].lower()
        if (skip or (sect, name) == here or not re.fullmatch(REFNAME, name)
                or LINE_BROKEN.search(m.string[max(0, m.start() - 16):m.start()])):
            return m[0]
        target = ref_target(name, sect, here[0])
        if target is None:
            unlinked.setdefault((name, sect), []).append(here[0])
            return m[0]
        if (target.sect, target.name) == here:
            return m[0]
        linked += 1
        href = html.escape(f"../{target.sect}/{pagefile(target.name)}")
        return f'<a href="{href}">{m[0]}</a>'
    return REF.sub(sub, body)


# ---- the top of a page ------------------------------------------------------------------------

def man_link(p, here_dir=".."):
    return f'<a href="{html.escape(f"{here_dir}/{p.sect}/{pagefile(p.name)}")}">{html.escape(p.name)}({p.sect.upper()})</a>'


def page_top(p, title):
    """Where the reader is, what the page is about, where it comes from, what else goes by its name."""
    out = [f'<p class="man-trail"><a href="../">Manual pages</a> › '
           f'<a href="./">{html.escape(section_label(p.sect))}</a></p>',
           f'<h2 class="man-title">{html.escape(title)}</h2>']
    if p.desc:
        out.append(f'<p class="man-desc">{html.escape(p.desc)}</p>')
    if p.path.startswith("/usr/share/"):
        out.append('<p class="man-from">From the original Amiga UNIX 2.1 manual. '
                   "Some things it mentions may not be in this release.</p>")
    else:
        out.append(f'<p class="man-from">Package: <code>{html.escape(p.pkg)}</code>, added for amigaux.</p>')
    out.extend(pair_notes(p))
    also = {}
    for n in [p.name] + p.others:
        for q in by_file.get(n, []) + by_file.get(n + ORIGINAL, []):
            if q is not p and q not in (original_of(p), package_of(p), aside_of(p), aside_base(p)):
                also[(q.sect, q.name)] = q
    if also:
        items = []
        for q in sorted(also.values(), key=lambda q: (section_key(q.sect), q.name)):
            what = ("the original page" if is_stock(q) and replaced_by.get(q.name[:-len(ORIGINAL)]
                    if q.name.endswith(ORIGINAL) else q.name) is p else section_names[q.sect])
            items.append(f"{man_link(q)}, {html.escape(what)}")
        out.append(f'<p class="man-also">Also by this name: {" · ".join(items)}</p>')
    out.append(search_box())
    return "\n".join(out)


def pair_notes(p):
    """What the reader's install shows: a replaced stock program, and a page kept in two forms."""
    base = p.name[:-len(ORIGINAL)] if p.name.endswith(ORIGINAL) else p.name
    cmd = p.sect in COMMAND_SECTS
    code = f"<code>{html.escape(base)}</code>"
    shown = replaced_by.get(base)
    if shown is not None and shown.sect != p.sect:
        shown = None
    out = []
    beside, under = aside_of(p), aside_base(p)
    if under is not None:
        tool = f"<code>/usr/apkg/bin/{html.escape(under.name)}</code>"
        out.append(f"This is apkg's own copy, {tool}, off the search path; "
                   f"<code>{html.escape(under.name)}</code> at the shell runs the original: "
                   f"see {man_link(under)}." if p.sect in COMMAND_SECTS else
                   f"apkg's own version of this page; the original is {man_link(under)}.")
    if beside is not None:
        out.append(f"apkg has its own copy, <code>/usr/apkg/bin/{html.escape(p.name)}</code>: "
                   f"see {man_link(beside)}." if p.sect in COMMAND_SECTS else
                   f"apkg's own version: {man_link(beside)}.")
    orig, added = original_of(p), package_of(p)
    if added is not None:                       # p is the kept original
        if shown is not None and shown is not p:
            out.append(f"In this release {code} runs {html.escape(shown.name)}: see {man_link(shown)}.")
        out.append(f"With the <code>{html.escape(added.pkg)}</code> package "
                   f"({package_sets[added.pkg]}), see {man_link(added)} instead.")
    elif orig is not None:                      # p took the name of an original page
        what = (f"{code} runs {html.escape(shown.name)}: see {man_link(shown)}"
                if cmd and shown is not None and shown is not p else
                f"{code} is the original one: see {man_link(orig)}" if cmd else
                f"the original page is {man_link(orig)}")
        if shown is not None and shown is not p:
            what += f"; the original page is {man_link(orig)}"
        out.append(f"This package comes {package_sets[p.pkg]}; without it, {what}.")
    elif shown is not None and shown is not p and is_stock(p):
        out.append(f"In this release {code} runs {html.escape(shown.name)}: see {man_link(shown)}.")
    return [f'<p class="man-from">{t}</p>' for t in out]


def search_box():
    return f'<div id="mansearch" class="man-search" data-base="{SITE_BASE}man/"></div>\n<script src="{SITE_BASE}man.js"></script>'


def jump_links(body):
    """A row of the page's own headings, on a long page."""
    heads = re.findall(r'<h1 class="Sh" id="([^"]+)">(.*?)</h1>', body, re.S)
    if len(body) < JUMP_FROM or len(heads) < 3:
        return ""
    links = " · ".join(f'<a href="#{i}">{FONT.sub("", re.sub(r"<[^>]+>", "", t))}</a>' for i, t in heads)
    return f'<p class="man-jump">{links}</p>\n'


BLANK_LINE = "\n\n"
reflow_faults = []


def changed_words(before, after):
    """Compare two renderings word by word: the same words, each with the same space around it. The
    one thing allowed is a word broken at a line end coming back together, with or without its
    hyphen; a dash standing alone is a word of its own. Returns where they first differ, or None."""
    def words(h):
        return html.unescape(re.sub(r"<[^>]+>", "", h)).split()
    a, b = words(before), words(after)
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i, j = i + 1, j + 1
            continue
        joined, k, found = a[i], i, False
        while re.search(r"\S[-_]$", joined) and k + 1 < len(a) and k - i < 4:
            k += 1
            whole, kept = joined[:-1] + a[k] if joined[-1] == "-" else None, joined + a[k]
            if b[j] in (whole, kept):
                found = True
                break
            joined = kept
        if not found:
            return f"{' '.join(a[i:i + 3])!r} became {' '.join(b[j:j + 3])!r}"
        i, j = k + 1, j + 1
    return None if i == len(a) and j == len(b) else f"the page ends differently, near {a[i:i + 2]} / {b[j:j + 2]}"


def ind(s_):
    return len(s_) - len(s_.lstrip())


def gaps_line_up(lines):
    gaps = [{m.start() for m in re.finditer(r"(?<=\S) {2,}(?=\S)", l)} for l in lines[:-1]]
    return len(gaps) > 1 and all(gaps) and bool(set.intersection(*gaps))


def may_be_table(lines):
    """nroff justifies text by stretching gaps at random; a table's gaps line up. Also kept as they
    are: blocks with a | and blocks with few ordinary words, such as lists of names and options."""
    words = " ".join(lines).split()
    ordinary = sum(1 for w in words if re.fullmatch(r"[a-z,.;:()'-]{2,}", w))
    return "|" in " ".join(lines) or gaps_line_up(lines) or ordinary / max(1, len(words)) < 0.5


def is_justified(lines, margin):
    """Text nroff filled: every line but the last ends at the page's right margin (a block's own
    edge could be chance), under one indent but for the first line. A first line further out is
    an entry, with a gap before the text below it lines up with."""
    if len(lines) < 2 or any(abs(len(l) - margin) > 1 for l in lines[:-1]) or len(lines[-1]) > margin + 1:
        return False
    if len({ind(l) for l in lines[1:]}) != 1:
        return False
    rest = ind(lines[1])
    return ind(lines[0]) >= rest or lines[0][max(0, rest - 2):rest] == "  "


def expand_tabs(line):
    """Tabs to spaces in a line of HTML, counting only what shows, so a table keeps its columns
    when the block's indent goes."""
    out, col, i = [], 0, 0
    while i < len(line):
        c = line[i]
        if c == "<":
            j = line.index(">", i) + 1
            out.append(line[i:j])
            i = j
            continue
        if c == "&":
            j = line.find(";", i)
            if j > 0 and j - i <= 6:
                out.append(line[i:j + 1])
                col += 1
                i = j + 1
                continue
        if c == "\t":
            n = 8 - col % 8
            out.append(" " * n)
            col += n
        else:
            out.append(c)
            col += 1
        i += 1
    return "".join(out)


def dedent(lines):
    """Lines of HTML without the indent they share, and that indent."""
    lines = [expand_tabs(l) for l in lines]
    shown = [FONT.sub("", l) for l in lines if FONT.sub("", l).strip()]
    n = min((ind(l) for l in shown), default=0)
    out = []
    for l in lines:
        m = re.match(r" *", l)
        out.append(l[min(n, m.end()):])
    return out, n


def join_words(left, right):
    """Join two lines of a paragraph. A word broken at the line end is put back, but for one the
    manual also writes with its hyphen (read-only)."""
    m = re.search(r"([A-Za-z]+)-((?:</[bi]>)?)$", left)
    n = re.match(r"((?:<[bi]>)?)([A-Za-z]+)", right)
    if m and n and (m[1][-1].islower() == n[2][0].islower()):
        whole, hyphened = (m[1] + n[2]).lower(), f"{m[1]}-{n[2]}".lower()
        if whole in corpus or hyphened not in corpus:
            return left[:m.start(1)] + m[1] + m[2] + right
        return left + right
    # A name broken after its _ or -; a dash standing alone stays a word of its own.
    if re.search(r"\S[_-]$", FONT.sub("", left)):
        return left + right
    return f"{left} {right}"


def keep_signs(text):
    """An underlined < or > may mean less or greater than or equal: nroff writes the two alike. In
    running text it stays underlined, as on the system, and nothing is assumed."""
    return re.sub(r"<i>(&[lg]t;)</i>", r"<u>\1</u>", text)


def looks_like_code(word):
    """An underlined or bold word in running text. nroff marks emphasis, names and options alike;
    only what cannot be a plain word goes in the code face: -c, \\n, /etc/passwd, $1, l, ECHO_2."""
    if word.rstrip(",.;:").lower() in ("an", "as", "at", "be", "by", "if", "in", "is", "it", "no", "of", "on", "or", "to"):
        return False
    return len(word) <= 2 or not re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*[,.;:]?", word)


def mark_words(text):
    """Set the marked words of a paragraph. A regular expression does not wrap: a break after its
    backslash reads as a space in it."""
    def sub(m):
        word = html.unescape(m[2])
        if not looks_like_code(word):
            return m[0]
        nowrap = " n" if "\\" in word and len(word) <= 30 else ""
        return f'<{m[1]} class="c{nowrap}">{m[2]}</{m[1]}>'
    return re.sub(r"<([bi])>([^<]*)</\1>", sub, text)


def paragraph(block, first_ind, rest_ind):
    term = None
    lines = [re.sub(r"[ \t]+", " ", l.strip()) for l in block]
    if first_ind < rest_ind:
        parts = re.split(r"(?<=\S)(?: {2,}|\t+)", block[0].strip(), maxsplit=1)
        if len(parts) == 2:
            term, lines[0] = parts[0], re.sub(r"[ \t]+", " ", parts[1])
    text = lines[0]
    for l in lines[1:]:
        text = join_words(text, l)
    cls = f"i{min(4, rest_ind // 4)}" + (" man-hang" if first_ind < rest_ind else "")
    if term is not None:
        text = f'<span class="man-term">{term}</span> {text}'
    return f'<p class="{cls}">{text}</p>'


ALL_BOLD = re.compile(r"\s*(?:<b>[^<]*</b>\s*)+")


def text_blocks(chunk, heading, margin):
    """A run of lines under one heading: paragraphs where it is plainly text, <pre> otherwise."""
    if heading in ("SYNOPSIS", "SYNTAX"):
        yield "\n".join(chunk), "wrap"
        return
    if heading == "NAME":
        text = ""
        for l in chunk:
            text = join_words(text, re.sub(r"\s+", " ", l.strip())) if text else re.sub(r"\s+", " ", l.strip())
        yield text, "i1"
        return

    def shown_of(lines):
        return [html.unescape(FONT.sub("", l)).expandtabs(8).rstrip() for l in lines]

    blocks, cur = [], []
    for l in chunk:
        if FONT.sub("", l).strip():
            cur.append(l)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    # A page break of the old printed form can fall inside a paragraph or a list entry: the line
    # before it is full and the next block carries on, in lower case, at the same indent or at the
    # column where the entry's text starts.
    merged = []
    for block in blocks:
        if merged:
            before, last, first = shown_of(merged[-1]), shown_of(merged[-1])[-1], shown_of(block)[0]
            at = ind(first)
            lines_up = at == ind(last) or (len(before) == 1 and at > ind(last) and last[max(0, at - 2):at] == "  ")
            if abs(len(last) - margin) <= 1 and lines_up and re.match(r"\s*[a-z(/]", first):
                merged[-1] = merged[-1] + block
                continue
        merged.append(block)

    items = []          # [text, kind, the (first, rest) indents of a list row that flows, a one-line block]
    for block in merged:
        shown = shown_of(block)
        # A sub-heading in bold, or an entry on a line of its own, above the text it heads.
        if len(block) > 1 and ind(shown[0]) < ind(shown[1]) and not is_justified(shown, margin):
            if ALL_BOLD.fullmatch(block[0]):
                items.append([block[0].strip(), f"i{min(4, ind(shown[0]) // 4)}", None, None])
                block, shown = block[1:], shown[1:]
            elif len(shown[0]) < margin - 3 and (is_justified(shown[1:], margin) or len(block) == 2):
                items.append([block[0], None, None, None])
                block, shown = block[1:], shown[1:]
        if len(block) == 1:
            # One line is text if it has no gaps and reads as text; a command or a name stays as it is.
            if (not re.search(r"\S {2,}\S|\S\t", shown[0].strip()) and re.search(r"[.:,]$", shown[0])
                    and not may_be_table(shown)):
                items.append([re.sub(r" +", " ", block[0].strip()), f"i{min(4, ind(shown[0]) // 4)}", None, None])
            else:
                items.append([block[0], None, None, block])
        elif is_justified(shown, margin) and not may_be_table(shown):
            first, rest = ind(shown[0]), ind(shown[1])
            items.append([paragraph(block, first, rest), "html", (first, rest) if first < rest else None, None])
        else:
            items.append(["\n".join(block), None, None, None])

    # The rows of one list go together: a one-line row beside a row that flows, with its text in
    # the same column and nothing else in columns, flows too.
    def same_list(item, row):
        first, rest = row
        line = shown_of(item[3])[0]
        return (ind(line) == first and len(line) > rest and line[rest - 2:rest] == "  " and line[rest] != " "
                and "|" not in line and not re.search(r"\S {2,}\S", line[rest:]))

    moved = True
    while moved:
        moved = False
        for i, item in enumerate(items):
            if item[3] is None:
                continue
            for near in (items[i - 1] if i else None, items[i + 1] if i + 1 < len(items) else None):
                if near is not None and near[2] and same_list(item, near[2]):
                    item[:] = [paragraph(item[3], *near[2]), "html", near[2], None]
                    moved = True
                    break
    for text_, kind, _, _ in items:
        yield text_, kind


def cat_body(text, here):
    """A preformatted page's text: its headings as headings, like mandoc's, justified text as
    paragraphs, the rest as it is. The build stops if a word has changed."""
    out, chunk, seen = [], [], {}
    heading = [""]
    widths = [len(html.unescape(FONT.sub("", l)).expandtabs(8).rstrip()) for l in text.split("\n")]
    margin = collections.Counter(w for w in widths if w >= 50).most_common(1)
    margin = margin[0][0] if margin else 65

    def flush():
        while chunk and not FONT.sub("", chunk[0]).strip():
            chunk.pop(0)
        while chunk and not FONT.sub("", chunk[-1]).strip():
            chunk.pop()
        if chunk:
            pre = []            # adjoining preformatted blocks stay one <pre>, as they were

            def end_pre():
                if pre:
                    lines, n = dedent(BLANK_LINE.join(pre).split("\n"))
                    out.append(f'<pre class="i{min(4, n // 4)}">{link_refs(chr(10).join(lines), here)}</pre>')
                    pre.clear()
            for piece, kind in text_blocks(list(chunk), heading[0], margin):
                if kind is None:
                    pre.append(piece)
                    continue
                end_pre()
                if kind == "wrap":
                    lines, n = dedent(piece.split("\n"))
                    out.append(f'<pre class="wrap i{min(4, n // 4)}">{link_refs(chr(10).join(lines), here)}</pre>')
                elif kind == "html":
                    out.append(mark_words(link_refs(keep_signs(piece), here)))
                else:
                    out.append(f'<p class="{kind}">{mark_words(link_refs(keep_signs(piece), here))}</p>')
            end_pre()
        chunk.clear()

    for line in text.split("\n"):
        plain_line = html.unescape(FONT.sub("", line)).rstrip()
        if "<b>" in line and re.fullmatch(r"[A-Z][A-Z0-9 /,.&()'-]+", plain_line):
            flush()
            heading[0] = plain_line
            ident = re.sub(r"[^A-Za-z0-9]+", "_", plain_line).strip("_")
            seen[ident] = seen.get(ident, 0) + 1
            if seen[ident] > 1:
                ident = f"{ident}_{seen[ident]}"
            out.append(f'<h1 class="Sh" id="{ident}">{html.escape(plain_line, quote=False)}</h1>')
        else:
            chunk.append(line)
    flush()
    result = "\n".join(out)

    wrong = changed_words(text, result)
    if wrong:
        reflow_faults.append((here, wrong))
    return result


def page_head(p):
    if not p.desc:
        return ""
    return f'<meta name="description" content="{html.escape(p.desc[:160])}">'


# ---- writing it out ---------------------------------------------------------------------------

# Words the manual writes whole or with a hyphen, mid-line, to tell a broken word from a compound.
corpus = set()
for p in man_pages:
    if p.kind == "cat":
        for l in plain(p.raw).split("\n"):
            corpus.update(re.findall(r"[a-z]+(?:-[a-z]+)*(?=[\s,.;:)])", l.lower()))

JUMP_FROM = 12000       # bytes of page text from which a page gets jump links
entries = {}            # section -> [(name, description, rendered?)]
skipped = 0
for p in man_pages:
    title = f"{p.name}({p.sect.upper()})"
    here = (p.sect, p.name)
    top = page_top(p, title)
    if p.kind == "cat":
        inner = cat_body(depaginate(p.raw), here)
        body = f'{top}\n{jump_links(inner)}<div class="man cat">{inner}</div>'
    else:
        if args.no_troff:
            entries.setdefault(p.sect, []).append((p.name, p.desc, False))
            skipped += 1
            continue
        r = subprocess.run([args.mandoc, "-T", "html", "-O", "fragment,man=../%S/%N.html"],
                           input=p.raw.encode("latin-1"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.returncode > 2:            # 1/2 are warnings and errors mandoc still renders
            sys.exit(f"man-html: mandoc failed on {p.sect}/{p.name}: {r.stderr.decode(errors='replace')}")
        text = r.stdout.decode("utf-8", "replace")
        text = re.sub(r'<table class="head">.*?</table>\s*', "", text, count=1, flags=re.S)
        inner = link_refs(text, here)
        body = f'{top}\n{jump_links(inner)}<div class="man">{inner}</div>'
    d = os.path.join(MAN, p.sect)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, pagefile(p.name)), "w", encoding="utf-8") as f:
        f.write(page(f"{title}: {p.desc[:70]}" if p.desc else title, body, page_head(p)))
    entries.setdefault(p.sect, []).append((p.name, p.desc, True))

if reflow_faults:
    for (sect, name), wrong in reflow_faults[:40]:
        print(f"man-html: reflowing changed {sect}/{name}: {wrong}", file=sys.stderr)
    sys.exit(f"man-html: reflowing changed the words of {len(reflow_faults)} pages")

with open(os.path.join(args.src, "refs-widened.tsv"), "w", encoding="utf-8") as f:
    for (name, sect, target), uses in sorted(widened.items()):
        f.write(f"{name}\t{sect}\t{target}\t{len(uses)}\t{','.join(sorted(set(uses)))}\n")
with open(os.path.join(args.src, "refs-unlinked.tsv"), "w", encoding="utf-8") as f:
    for (name, sect), uses in sorted(unlinked.items()):
        f.write(f"{name}\t{sect}\t{len(uses)}\t{','.join(sorted(set(uses)))}\n")

for sect, items in entries.items():
    rows_html = []
    for name, desc, ok in sorted(items, key=lambda x: x[0].lower()):
        cell = (f'<a href="{html.escape(pagefile(name))}"><code>{html.escape(name)}</code></a>' if ok
                else f"<code>{html.escape(name)}</code>")
        rows_html.append(f"<tr><td>{cell}</td><td>{html.escape(desc)}</td></tr>")
    body = (f'<p class="man-trail"><a href="../">Manual pages</a></p>\n'
            f"<h2>{html.escape(section_label(sect))}</h2>\n{search_box()}\n"
            f'<div class="tbl man-index"><table>\n' + "\n".join(rows_html) + "\n</table></div>")
    os.makedirs(os.path.join(MAN, sect), exist_ok=True)
    with open(os.path.join(MAN, sect, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(section_label(sect), body))

for name in short_names:
    p = short_target(name)
    href = html.escape(f"../{p.sect}/{pagefile(p.name)}")
    d = os.path.join(MAN, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"><!--man-stub-->\n'
                f'<title>{html.escape(name)}: manual page</title>\n'
                '<meta name="robots" content="noindex,follow">\n'
                f'<meta http-equiv="refresh" content="0; url={href}">\n'
                f'<link rel="canonical" href="{href}"></head>\n'
                f'<body><p><a href="{href}">{html.escape(p.name)}({p.sect.upper()})</a></p></body></html>\n')

# ---- A-Z: plain lists, for old browsers that draw a table only when all of it has arrived --------

def letter_of(name):
    c = name[0].lower()
    return c if "a" <= c <= "z" else "other"


def az_rows(pages_, up):
    rows_ = []
    for p in pages_:
        other = f' <span class="man-other">also {html.escape(", ".join(p.others))}</span>' if p.others else ""
        desc = f" {html.escape(p.desc)}" if p.desc else ""
        rows_.append(f'<li><a href="{up}{p.sect}/{pagefile(p.name)}">{html.escape(p.name)}({p.sect.upper()})</a>{desc}{other}</li>')
    return '<ul class="man-list">\n' + "\n".join(rows_) + "\n</ul>"


by_name = sorted(man_pages, key=lambda p: (p.name.lower(), section_key(p.sect)))
letters = {}
for p in by_name:
    letters.setdefault(letter_of(p.name), []).append(p)


def az_nav(up):
    return ('<p class="man-az">' + " ".join(f'<a href="{up}{c}/">{c.upper() if c != "other" else "Other"}</a>'
                                            for c in sorted(letters)) + "</p>")


os.makedirs(os.path.join(MAN, "names"), exist_ok=True)
with open(os.path.join(MAN, "names", "index.html"), "w", encoding="utf-8") as f:
    f.write(page("Manual pages A-Z", f'<p class="man-trail"><a href="../">Manual pages</a></p>\n'
                 f"<h2>All pages A–Z</h2>\n{search_box()}\n<p>Every page on one page, for your browser's Find.</p>\n"
                 f'{az_nav("")}\n{az_rows(by_name, "../")}'))
for c, ps in letters.items():
    os.makedirs(os.path.join(MAN, "names", c), exist_ok=True)
    label = c.upper() if c != "other" else "Other"
    with open(os.path.join(MAN, "names", c, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(f"Manual pages: {label}", f'<p class="man-trail"><a href="../../">Manual pages</a> › '
                     f'<a href="../">All pages A–Z</a></p>\n<h2>{label}</h2>\n{az_nav("../")}\n{az_rows(ps, "../../")}'))

# ---- the landing page --------------------------------------------------------------------------

tasks = {}      # group -> [(task, link, name shown)]
for group, task, target, *_ in read_table("man-tasks.tsv"):
    if target.startswith("site:"):
        path = target[5:]
        if not os.path.isfile(os.path.join(args.site, path, "index.html")):
            sys.exit(f"man-html: a common task points at a page the site does not have: {path}")
        tasks.setdefault(group, []).append((task, f"../{path}", None))
    else:
        sect, name = target.split("/")
        if (sect, name) not in by_key:
            sys.exit(f"man-html: a common task points at a man page not in this release: {target}")
        tasks.setdefault(group, []).append((task, f"{sect}/{pagefile(name)}", name))

idx = os.path.join(MAN, "index.html")
with open(idx, encoding="utf-8") as f:
    landing = f.read()
parts = [search_box(), '<p class="man-lookup">Know the command? Add its name to the address: '
         '<a href="tar/"><code>/man/tar</code></a>.</p>',
         "<h3>Common tasks</h3>", '<div class="man-groups">']
for group, items in tasks.items():
    lis = "\n".join(f'  <li><a href="{html.escape(link)}">{html.escape(task)}</a>'
                    + (f" <code>{html.escape(name)}</code>" if name else "") + "</li>"
                    for task, link, name in items)
    parts.append(f"<div><h4>{html.escape(group)}</h4>\n<ul>\n{lis}\n</ul></div>")
parts += ["</div>", "<h3>All pages A–Z</h3>", az_nav("names/"),
          '<p><a href="names/">Every page on one page</a>, with its description, for your browser\'s Find.</p>',
          "<h3>By kind</h3>", '<div class="man-groups">']
for group, codes in groups.items():
    lis = "\n".join(f'  <li><a href="{s}/">{html.escape(section_label(s))}</a>: '
                    f'{len(entries[s])} page{"" if len(entries[s]) == 1 else "s"}</li>'
                    for s in codes if s in entries)
    if lis:
        parts.append(f"<div><h4>{html.escape(group)}</h4>\n<ul>\n{lis}\n</ul></div>")
parts.append("</div>")
if "<!--MANSECTIONS-->" not in landing:
    sys.exit(f"man-html: {idx} lacks <!--MANSECTIONS-->")
css = re.search(r'<link rel="stylesheet" href="[^"]*man\.css">', frame)[0]
with open(idx, "w", encoding="utf-8") as f:
    f.write(landing.replace("<!--MANSECTIONS-->", "\n".join(parts)).replace("</head>", f"{css}\n</head>", 1))
os.remove(FRAME)

# ---- the search index: one line per page, loaded only when someone searches -----------------------
# name, section, own name not man(1)'s choice, other names that lead here, other names that do not,
# task words, description, address (site pages only).
task_words = {}
for group, task, target, *more in read_table("man-tasks.tsv"):
    task_words.setdefault(target, []).append(more[0] if more else task)


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


lines = []
for p in sorted(man_pages, key=lambda p: (section_key(p.sect), len(p.name), p.name)):
    won = [n for n in p.others if short_target(n) is p]
    lost = [n for n in p.others if short_target(n) is not p]
    words = " ".join(task_words.get(f"{p.sect}/{p.name}", []))
    lines.append("\t".join((p.name, p.sect, "" if short_target(p.name) is p else "1",
                            " ".join(won), " ".join(lost), words.lower(), clean(p.desc), "")))
for d, _, files in sorted(os.walk(args.site)):
    rel = os.path.relpath(d, args.site).replace(os.sep, "/")
    if "index.html" not in files or rel == "." or rel == "man" or rel.startswith("man/"):
        continue
    with open(os.path.join(d, "index.html"), encoding="utf-8") as f:
        m = re.search(r"<title>(.*?)(?: — [^<]*)?</title>", f.read(), re.S)
    if m and m[1].strip():
        words = " ".join(task_words.get(f"site:{rel}/", []))
        title = clean(html.unescape(m[1]))
        lines.append("\t".join((title, "", "", "", "", words.lower(), title, f"../{rel}/")))
sect_names = {s: section_names[s] for s in entries}
with open(os.path.join(MAN, "index.js"), "w", encoding="utf-8") as f:
    f.write("MANIDX=" + json.dumps("\n".join(lines)) + ";\nMANSECT=" + json.dumps(sect_names, separators=(",", ":")) + ";\n")

# ---- the site's own pages link in -----------------------------------------------------------------
# `name(section)` in a page's Markdown becomes a link. One that has no page is left for
# tools/check-site.py to refuse. Links and code blocks are not touched.
SITE_REF = re.compile(rf"<a\b.*?</a>|<code>({REFNAME})\(({REFSECT})\)</code>", re.S)
site_links = 0


def link_site(text, d):
    def sub(m):
        global site_links
        if not m[1]:
            return m[0]
        target = ref_target(m[1], m[2].lower(), "site")
        if target is None:
            return m[0]
        site_links += 1
        href = os.path.relpath(os.path.join(MAN, target.sect, pagefile(target.name)), d).replace(os.sep, "/")
        return f'<a href="{html.escape(href)}">{m[0]}</a>'
    return SITE_REF.sub(sub, text)


for d, _, files in os.walk(args.site):
    rel = os.path.relpath(d, args.site).replace(os.sep, "/")
    if rel == "man" or rel.startswith("man/"):
        continue
    for name in files:
        if name.endswith(".html"):
            path = os.path.join(d, name)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            new = link_site(text, d)
            if new != text:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)

# MkDocs wrote the sitemap before these pages existed. (The preview has none.)
sitemap = os.path.join(args.site, "sitemap.xml")
if os.path.exists(sitemap):
    with open(sitemap, encoding="utf-8") as f:
        xml = f.read()
    m = re.search(r"<loc>([^<]*/)man/</loc>", xml)
    if not m:
        sys.exit("man-html: sitemap.xml does not list /man/")
    urls = [f"man/{s}/" for s in entries] + [f"man/{p.sect}/{pagefile(p.name)}" for p in man_pages]
    more = "".join(f"<url><loc>{m.group(1)}{html.escape(u)}</loc></url>\n" for u in urls)
    xml = xml.replace("</urlset>", more + "</urlset>")
    with open(sitemap, "w", encoding="utf-8") as f:
        f.write(xml)
    with open(sitemap + ".gz", "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as gz:
            gz.write(xml.encode("utf-8"))

n = sum(len(v) for v in entries.values())
print(f"man-html: {n} pages in {len(entries)} sections, {len(short_names)} short addresses, {linked} cross references linked "
      f"({sum(len(u) for u in widened.values())} by the same-number rule, {len(widened)} distinct), "
      f"{site_links} from the site's pages"
      + (f"; {skipped} troff pages not rendered (--no-troff)" if skipped else ""))
