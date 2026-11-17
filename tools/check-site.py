#!/usr/bin/env python3
"""Check a built site before it is deployed.

usage: check-site.py [--allow-placeholders] <built site dir>
       check-site.py --preview <base path> <built site dir>

Fails (exit 1) on:
  - a PLACEHOLDER marker anywhere: invented draft text must never go live
    (--allow-placeholders turns this one into a warning; only on purpose);
  - a third-party request: any src=, stylesheet or icon href, or CSS url() that
    leaves the site (links people click may go anywhere; what a page loads may not);
  - a broken internal link or anchor, including links written as HTML in the pages;
  - a local file a page or the stylesheet loads (font, image, icon) that is not in the build;
  - a page naming a man page with `name(section)` that this release does not have, once the man
    pages are built: tools/man-html.py links the ones it finds (a warning in the preview).
Links into the server-only trees (/files/, /stats/, /sakuuu/, /video/) are not
checked: they are not part of the build.

A man page's short address (/man/<name>/, marked <!--man-stub-->) is a small redirecting file with
no frame: it is noindexed in every build and its link is checked like any other.

A normal build must carry no preview marks (the robots noindex line, the banner). With
--preview <base> (tools/build.sh --preview) every page must carry both, the placeholders must
have become TBD (counted, not refused), there is no sitemap, and every local path a page
names lies under <base>; a link to the published site (https://amigaux.org/...) is let through.
"""
import os
import posixpath
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlsplit

USAGE = "usage: check-site.py [--allow-placeholders | --preview <base path>] <built site dir>"
ARGS = sys.argv[1:]
ALLOW_PH = "--allow-placeholders" in ARGS
ARGS = [a for a in ARGS if a != "--allow-placeholders"]
BASE, PREVIEW = "/", False
if ARGS[:1] == ["--preview"]:
    if len(ARGS) < 2 or not (ARGS[1].startswith("/") and ARGS[1].endswith("/")) or ARGS[1] == "/":
        sys.exit(USAGE)
    BASE, PREVIEW, ARGS = ARGS[1], True, ARGS[2:]
if len(ARGS) != 1:
    sys.exit(USAGE)
ROOT = ARGS[0]
NOINDEX = '<meta name="robots" content="noindex,nofollow">'
BANNER = 'class="preview-banner"'
tbd = 0
stubs = 0
SELF = ("amigaux.org", "www.amigaux.org")
SERVER_ONLY = ("/files/", "/stats/", "/sakuuu/", "/video/")
errors = []


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.loads = set(), [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if "src" in a:
            self.loads.append(a["src"])
        if tag == "link" and "href" in a:
            self.loads.append(a["href"])

    handle_startendtag = handle_starttag


pages = {}
local = []  # (file, URL) of everything loaded from the site itself
for d, _, files in os.walk(ROOT):
    for f in files:
        path = os.path.join(d, f)
        rel = "/" + os.path.relpath(path, ROOT).replace(os.sep, "/")
        if f.endswith((".html", ".css", ".xml", ".txt")):
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            stub = f.endswith(".html") and "<!--man-stub-->" in text
            if stub:
                stubs += 1
                if '<meta name="robots" content="noindex,follow">' not in text:
                    errors.append(f"{rel}: a short address that is not noindexed")
            elif f.endswith(".html"):
                marks = (NOINDEX in text, BANNER in text)
                if PREVIEW and marks != (True, True):
                    errors.append(f"{rel}: lacks the preview marks (robots noindex, banner)")
                if not PREVIEW and any(marks):
                    errors.append(f"{rel}: carries a preview mark in a normal build")
                if PREVIEW:
                    tbd += text.count("TBD")
            if "PLACEHOLDER" in text:
                if PREVIEW:
                    errors.append(f"{rel}: a PLACEHOLDER marker not shown as TBD")
                elif ALLOW_PH:
                    print(f"check-site: WARNING: {rel} carries a PLACEHOLDER marker (allowed on purpose)",
                          file=sys.stderr)
                else:
                    errors.append(f"{rel}: carries a PLACEHOLDER marker")
            if f.endswith(".css"):
                for u in re.findall(r"url\(\s*['\"]?([^'\")]+)", text):
                    if urlsplit(u).netloc:
                        errors.append(f"{rel}: CSS loads {u}")
                    else:
                        local.append((rel, u))
            if f.endswith(".html"):
                p = Page()
                p.feed(text)
                pages[rel] = p
                for u in p.loads:
                    if urlsplit(u).netloc:
                        errors.append(f"{rel}: loads {u}")
                    else:
                        local.append((rel, u))


def inside(path):
    """A path the browser asks the server for, as a path in the build; None if outside BASE."""
    if not path.startswith(BASE):
        return None
    return "/" + path[len(BASE):]


def target(page, href):
    """The local path and fragment an internal link points at, or None for an external one."""
    s = urlsplit(href)
    if s.scheme in ("mailto", "tel"):
        return None
    if s.netloc and s.netloc not in SELF:
        return None
    path = s.path
    if path.startswith("/"):
        path = inside(path)
        if path is None:
            if PREVIEW and s.netloc:
                return None                     # the published site, on purpose
            errors.append(f"{page}: {href} lies outside {BASE}")
            return None
    if not s.netloc and not path.startswith("/"):
        path = posixpath.normpath(posixpath.join(posixpath.dirname(page), path or posixpath.basename(page)))
        if (href.split("#")[0].endswith("/") or not href.split("#")[0]) and not path.endswith("/"):
            path += "/" if not path.endswith(".html") else ""
    return path or "/", s.fragment


for page, p in sorted(pages.items()):
    for href in p.links:
        t = target(page, href)
        if t is None:
            continue
        path, frag = t
        if path.startswith(SERVER_ONLY):
            continue
        if path.endswith("/"):
            file = path + "index.html"
        elif os.path.isdir(os.path.join(ROOT, path.lstrip("/"))):
            errors.append(f"{page}: {href} names a directory without the trailing slash")
            continue
        else:
            file = path
        if not os.path.isfile(os.path.join(ROOT, file.lstrip("/"))):
            errors.append(f"{page}: {href} -> {file} does not exist")
        elif frag and file in pages and frag not in pages[file].ids:
            errors.append(f"{page}: {href} -> no id \"{frag}\" in {file}")

if os.path.isdir(os.path.join(ROOT, "man", "1")):
    for rel in sorted(pages):
        if rel.startswith("/man/"):
            continue
        with open(os.path.join(ROOT, rel.lstrip("/")), encoding="utf-8") as fh:
            text = re.sub(r"<a\b.*?</a>", "", fh.read(), flags=re.S)
        for name in re.findall(r"<code>([A-Za-z_][\w.+-]*\(\d[A-Za-z]*\))</code>", text):
            if PREVIEW:
                print(f"check-site: WARNING: {rel} names {name}, which has no man page", file=sys.stderr)
            else:
                errors.append(f"{rel} names {name}, which has no man page")

for rel, u in local:
    path = urlsplit(u).path
    if path.startswith("/"):
        path = inside(path)
        if path is None:
            errors.append(f"{rel}: loads {u}, outside {BASE}")
            continue
    else:
        path = posixpath.normpath(posixpath.join(posixpath.dirname(rel), path))
    if not os.path.isfile(os.path.join(ROOT, path.lstrip("/"))):
        errors.append(f"{rel}: loads {u}, which is not in the build")

if not pages:
    errors.append(f"no pages under {ROOT}")
if PREVIEW and os.path.exists(os.path.join(ROOT, "sitemap.xml")):
    errors.append("sitemap.xml in a preview build")
for e in errors:
    print("check-site:", e, file=sys.stderr)
if errors:
    sys.exit(1)
if PREVIEW:
    ph = f"preview at {BASE}: noindex and banner on every page, {tbd} TBD marks"
else:
    ph = "placeholders allowed on purpose" if ALLOW_PH else "no placeholders"
extra = f" and {stubs} short addresses" if stubs else ""
print(f"check-site: {len(pages) - stubs} pages{extra} OK ({ph}, no third-party loads, local files present, internal links and anchors resolve)")
