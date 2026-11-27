#!/usr/bin/env python3
"""Check /man/ in a real browser. Run by hand before a batch; not part of the build, since it needs
Playwright and Chromium. Tests the build in build/site, whichever kind it is.

usage: man-browser-test.py [--all]    --all also opens every page for the phone-width check

  - the search index in parts: a common search loads no programming part; a search that finds
    nothing elsewhere loads them by itself
  - the search questions in tools/man-search-questions.tsv: right page in the top five, and how many first
  - typing in the box, and Enter going to the first result
  - JavaScript off: landing page, A-Z, a short address and a page all work, with no search box
  - no page wider than a 390 px phone (a sample, or all with --all)
  - no script errors
"""
import functools
import http.server
import os
import random
import re
import sys
import tempfile
import threading
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "build", "site")
with open(os.path.join(SITE, "man", "index.html"), encoding="utf-8") as f:
    m = re.search(r'href="([^"]*)man\.css"', f.read())
BASE = m[1]          # "/" or "/preview/"
root = tempfile.mkdtemp(prefix="man-test")
os.symlink(os.path.realpath(SITE), os.path.join(root, BASE.strip("/"))) if BASE != "/" else None
serve = os.path.realpath(SITE) if BASE == "/" else root


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=serve))
threading.Thread(target=server.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{server.server_address[1]}{BASE}"
fails = []
with open(os.path.join(HERE, "man-search-questions.tsv"), encoding="utf-8") as f:
    questions = [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/chromium", args=["--disable-gpu", "--disable-dev-shm-usage"])
    pg = b.new_page(viewport={"width": 1200, "height": 800})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL + "man/")
    pg.fill("#mansearch-q", "")
    pg.type("#mansearch-q", "copy files")
    pg.wait_for_selector("#mansearch ol li:first-child a[href$='/1/cp.html']")
    pg.wait_for_function("!MANBUSY()")
    fetched = "performance.getEntriesByType('resource').map(e => e.name).filter(n => /index-programming/.test(n)).length"
    if pg.evaluate(fetched):
        fails.append("a search for 'copy files' loaded the programming pages")
    if "programming pages too" not in pg.inner_text("#mansearch .man-status"):
        fails.append("no offer to search the programming pages too")
    pg.fill("#mansearch-q", "")
    pg.type("#mansearch-q", "strcpy")
    pg.wait_for_selector("#mansearch ol li a[href$='/string.html']")
    if not pg.evaluate(fetched):
        fails.append("a search for 'strcpy' found it without loading the programming pages")
    print("parts: 'copy files' from the first parts; 'strcpy' loaded the programming pages by itself")
    pg.wait_for_function("!MANBUSY()")
    first = top5 = 0
    for q, want in questions:
        got = pg.evaluate("q => { document.getElementById('mansearch-q').value = q; return MANSEARCH(q); }", q)
        accepted = want.split()
        a = bool(got) and got[0] in accepted
        c = any(n in accepted for n in got[:5])
        first += a
        top5 += c
        if not c:
            fails.append(f"search {q!r}: wanted {want}, got {got[:5]}")
        elif not a:
            print(f"  not first: {q!r} wanted {want}, got {got[:3]}")
    print(f"search: {first} first, {top5} in the top five, of {len(questions)}")
    pg.fill("#mansearch-q", "")
    pg.type("#mansearch-q", "copy files")
    pg.wait_for_selector("#mansearch ol li:first-child a[href$='/1/cp.html']")
    print("  typed:", pg.inner_text("#mansearch ol li:first-child")[:90])
    pg.press("#mansearch-q", "Enter")
    pg.wait_for_url("**/man/1/cp.html")
    pg.goto(URL + "man/1/ls.html")
    pg.fill("#mansearch-q", "sound")
    pg.wait_for_selector("#mansearch ol li")
    if "../docs/sound" not in pg.get_attribute("#mansearch ol li:first-child a", "href"):
        fails.append("search for sound on a man page does not lead to the Sound page")
    pg.goto(URL + "man/tar/")
    pg.wait_for_url("**/man/1/heirloom-tar.html")
    if errs:
        fails.append(f"script errors: {errs[:3]}")

    ctx = b.new_context(java_script_enabled=False, viewport={"width": 1200, "height": 800})
    off = ctx.new_page()
    for path, must in (("man/", "Common tasks"), ("man/names/", "All pages"), ("man/names/t/", "tar"), ("man/1/ls.html", "list contents")):
        off.goto(URL + path)
        text = off.inner_text("main")
        if must.lower() not in text.lower():
            fails.append(f"JavaScript off: /{path} lacks {must!r}")
        if off.query_selector("#mansearch input"):
            fails.append(f"JavaScript off: /{path} shows a search box")
    off.goto(URL + "man/tar/")
    off.wait_for_url("**/man/1/heirloom-tar.html", timeout=5000)
    print("JavaScript off: landing, A-Z, a page and a short address work; no search box")

    rows = []
    with open(os.path.join(HERE, "..", "build", "man-src", "manifest.tsv"), encoding="utf-8") as f:
        for line in f:
            r = line.rstrip("\n").split("\t")
            rows.append(f"man/{r[1]}/{'index-page' if r[2] == 'index' else r[2]}.html")
    extra = ["man/", "man/names/", "man/names/x/", "man/1m/", "man/3x/"]
    chosen = rows if "--all" in sys.argv else random.Random(1).sample(rows, 150)
    ph = b.new_page(viewport={"width": 390, "height": 800})
    wide = []
    for path in extra + chosen:
        ph.goto(URL + path, wait_until="load")
        w = ph.evaluate("document.documentElement.scrollWidth")
        if w > 390:
            wide.append((w, path))
    print(f"phone: {len(wide)} of {len(extra) + len(chosen)} pages wider than 390 px", sorted(wide, reverse=True)[:8])
    if wide:
        fails.append("pages wider than a phone")
    b.close()
server.shutdown()
for f in fails:
    print("man-browser-test:", f, file=sys.stderr)
sys.exit(1 if fails else 0)
