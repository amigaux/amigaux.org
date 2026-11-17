#!/usr/bin/env python3
"""Period (1990-92) logo concepts for AMIGA UNIX -- amigaux.org identity, NOT a demo asset.
Brief (2026-09-17): original shapes only (no C=, tick, Boing); AMIGA UNIX one line + '68040 · 68060';
built for the black page + Oswald headline; white/silver + ONE red rule; favicon = single A + red rule.
  c1-stripes    hand-built extended caps cut into 8 workstation scan-line bars; the red rule is the 9th bar
  c2-nameplate  the same caps, solid brushed metal on a dark bezelled case badge
  c3-boxcover   Oswald SemiBold outlines (the page's own face) under a heavy red rule, spec line flush-left
Every glyph is converted to outlines: the SVGs have no font dependency. Run with ./venv/bin/python gen.py"""
import os, math, functools, subprocess, shutil
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
RED = '#d62d2d'
SPEC = '68040 · 68060'

# ---------------------------------------------------------------- geometry helpers
def rrect(x0, y0, x1, y1, r):
    tl, tr, br, bl = r if isinstance(r, (tuple, list)) else (r, r, r, r)
    def arc(cx, cy, rad, a0, a1, n=14):
        if rad <= 0: return [(cx, cy)]
        return [(cx + rad * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                 cy + rad * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    return Polygon(arc(x0 + tl, y0 + tl, tl, 180, 270) + arc(x1 - tr, y0 + tr, tr, 270, 360) +
                   arc(x1 - br, y1 - br, br, 0, 90) + arc(x0 + bl, y1 - bl, bl, 90, 180))

def polys(g):
    if g.is_empty: return []
    if g.geom_type == 'Polygon': return [g]
    return [p for sub in getattr(g, 'geoms', []) for p in polys(sub)]

def num(v): s = f'{v:.2f}'.rstrip('0').rstrip('.'); return '0' if s in ('-0', '') else s

def pathd(g, dx=0, dy=0):
    d = []
    for p in polys(g):
        for ring in [p.exterior, *p.interiors]:
            c = list(ring.coords)[:-1]
            if len(c) >= 3: d.append('M' + ' '.join(f'{num(x + dx)} {num(y + dy)}' for x, y in c) + 'Z')
    return ''.join(d)

# ---------------------------------------------------------------- the hand-built extended caps (cap height 100, stroke ~24)
def L_A():
    outer = Polygon([(0, 100), (41, 0), (69, 0), (110, 100)])
    counter = Polygon([(42.6, 62), (55, 31.7), (67.4, 62)])
    notch = Polygon([(35.2, 80), (74.8, 80), (83.2, 100.5), (26.8, 100.5)])
    return outer.difference(counter).difference(notch), 110
def L_M():
    return unary_union([box(0, 0, 24, 100), box(106, 0, 130, 100),
                        Polygon([(0, 0), (30, 0), (80, 72), (50, 72)]),
                        Polygon([(100, 0), (130, 0), (80, 72), (50, 72)])]), 130
def L_I(): return box(0, 0, 24, 100), 24
def L_G():
    outer = rrect(0, 0, 104, 100, 34); inner = rrect(24, 24, 80, 76, 10)
    ring = outer.difference(inner).difference(box(70, 24, 110, 50)).difference(box(88, -1, 110, 24.01))
    return ring.union(box(54, 50, 104, 76)).intersection(outer), 104
def L_U():
    return rrect(0, 0, 100, 100, (0, 0, 34, 34)).difference(rrect(24, -10, 76, 76, (0, 0, 10, 10))), 100
def L_N():
    return unary_union([box(0, 0, 24, 100), box(76, 0, 100, 100),
                        Polygon([(0, 0), (30, 0), (100, 100), (70, 100)])]), 100
def L_X():
    return unary_union([Polygon([(0, 0), (30, 0), (104, 100), (74, 100)]),
                        Polygon([(74, 0), (104, 0), (30, 100), (0, 100)])]), 104
CAPS = {'A': L_A, 'M': L_M, 'I': L_I, 'G': L_G, 'U': L_U, 'N': L_N, 'X': L_X}

def word(text, track=15, space=46):
    x, parts, prev = 0, [], None
    for ch in text:
        if ch == ' ': x += space - track; continue
        g, w = CAPS[ch](); parts.append(affinity.translate(g, x, 0)); x += w + track
    return unary_union(parts), x - track

def bars(y0, n, bar, gap, x0, x1):
    return unary_union([box(x0, y0 + i * (bar + gap), x1, y0 + i * (bar + gap) + bar) for i in range(n)])

# ---------------------------------------------------------------- Oswald SemiBold outlines (SIL OFL, the site's own face)
class FlatPen(BasePen):
    def __init__(self, gs): super().__init__(gs); self.contours, self.cur = [], []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, 9):
            t = i / 8; m = 1 - t
            self.cur.append(tuple(m**3 * p0[k] + 3 * m * m * t * p1[k] + 3 * m * t * t * p2[k] + t**3 * p3[k] for k in (0, 1)))
    def _closePath(self):
        if len(self.cur) > 2: self.contours.append(self.cur)
        self.cur = []
    _endPath = _closePath

FONT = TTFont(os.path.join(HERE, 'oswald-600-latin.woff2'))
GS, CMAP, HMTX = FONT.getGlyphSet(), FONT.getBestCmap(), FONT['hmtx']
def oswald(text, cap, track_em=0.0):
    """Outlines with the cap top at y=0 and the leftmost ink at x=0; returns (geom, ink width)."""
    s, x, geoms = cap / 810.0, 0.0, []
    for ch in text:
        gn = CMAP[ord(ch)]; pen = FlatPen(GS); GS[gn].draw(pen)
        ps = [Polygon([(x + px * s, (810 - py) * s) for px, py in c]) for c in pen.contours]
        ps = [p if p.is_valid else p.buffer(0) for p in ps]
        if ps: geoms.append(functools.reduce(lambda a, b: a.symmetric_difference(b), ps))
        x += HMTX[gn][0] * s + track_em * 1000 * s
    g = unary_union(geoms); minx, _, maxx, _ = g.bounds
    return affinity.translate(g, -minx, 0), maxx - minx

# ---------------------------------------------------------------- hand-set 16 px favicon letters (outlines don't land on a 16 px grid)
A_WIDE = ['....###....', '....###....', '...##.##...', '...##.##...', '..##...##..', '..##...##..',
          '.#########.', '.##.....##.', '##.......##', '##.......##', '##.......##']
A_NARROW = ['...###...', '...###...', '..##.##..', '..##.##..', '..##.##..', '.##...##.',
            '.#######.', '.##...##.', '##.....##', '##.....##']
def pixels(rows, x0, y0, skip=()):
    return unary_union([box(x0 + x, y0 + y, x0 + x + 1, y0 + y + 1) for y, r in enumerate(rows) if y not in skip
                        for x, c in enumerate(r) if c == '#'])

# ---------------------------------------------------------------- SVG writers
def svg(vb, body, defs=''):
    x, y, w, h = vb
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{num(x)} {num(y)} {num(w)} {num(h)}" '
            f'width="{num(w)}" height="{num(h)}" role="img" aria-label="Amiga Unix">'
            f'<title>AMIGA UNIX</title>{("<defs>" + defs + "</defs>") if defs else ""}{body}</svg>\n')
def path(g, fill, dx=0, dy=0, extra=''):
    return f'<path fill="{fill}" fill-rule="evenodd"{extra} d="{pathd(g, dx, dy)}"/>'
def write(rel, text):
    p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(text); return p

# ---------------------------------------------------------------- concept 1: workstation stripes
def c1():
    name, W = word('AMIGA UNIX')
    striped = name.intersection(bars(0, 8, 9, 4, -5, W + 5))       # 8 bars, 9 on / 4 off = 100 units
    rule = box(0, 104, W, 113)                                       # the 9th bar, in red, full width
    spec, sw = oswald(SPEC, 23, 0.32)
    P, top = 6, 133
    vb = (-P, -P, W + 2 * P, top + 23 + 2 * P)
    for tone, fg, dim in (('dark', '#f2f2f2', '#a6a6a6'), ('light', '#141414', '#5a5a5a')):
        write(f'c1-stripes/amiga-unix-stripes-{tone}.svg', svg(vb,
              path(striped, fg) + path(rule, RED) + path(spec, dim, (W - sw) / 2, top)))
    A, _ = L_A()
    def fav(G):
        if G == 16:   # the pixel A with every other row blanked = one-pixel scan lines
            return svg((0, 0, 16, 16), path(rrect(0, 0, 16, 16, 2), '#000') + path(pixels(A_WIDE, 2, 1, skip=(1, 3, 5, 7, 9)), '#f2f2f2') + path(box(2, 13, 13, 15), RED))
        a = affinity.translate(affinity.scale(A, 20 / 110, 18 / 100, origin=(0, 0)), 6, 4); b = bars(4, 4, 3, 2, 0, 32); r = box(6, 25, 26, 28)
        return svg((0, 0, G, G), path(rrect(0, 0, G, G, 6), '#000') + path(a.intersection(b), '#f2f2f2') + path(r, RED))
    return vb, fav

# ---------------------------------------------------------------- concept 2: case nameplate
def c2():
    name, W = word('AMIGA UNIX')
    spec, sw = oswald(SPEC, 21, 0.32)
    PX, PT, PB = 48, 38, 34
    rule = box(0, 121, W, 125); top = 141; bottom = top + 21 + PB
    outer = rrect(-PX, -PT, W + PX, bottom, 20); inner = rrect(-PX + 6, -PT + 6, W + PX - 6, bottom - 6, 15)
    defs = (f'<linearGradient id="bezel" gradientUnits="userSpaceOnUse" x1="0" y1="{-PT}" x2="0" y2="{bottom}">'
            '<stop offset="0" stop-color="#ededed"/><stop offset=".48" stop-color="#9a9a9a"/><stop offset=".52" stop-color="#6c6c6c"/>'
            '<stop offset="1" stop-color="#c4c4c4"/></linearGradient>'
            f'<linearGradient id="plate" gradientUnits="userSpaceOnUse" x1="0" y1="{-PT}" x2="0" y2="{bottom}">'
            '<stop offset="0" stop-color="#2b2b2b"/><stop offset="1" stop-color="#101010"/></linearGradient>'
            '<linearGradient id="metal" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="100">'
            '<stop offset="0" stop-color="#ffffff"/><stop offset=".46" stop-color="#d6d6d6"/><stop offset=".5" stop-color="#a2a2a2"/>'
            '<stop offset=".8" stop-color="#c2c2c2"/><stop offset="1" stop-color="#ececec"/></linearGradient>')
    body = (path(outer, 'url(#bezel)') + path(inner, 'url(#plate)', extra=' stroke="#000" stroke-width="1.5"') +
            path(name, '#000', 0, 3.5) + path(name, '#ffffff', 0, -1.2, ' fill-opacity=".35"') + path(name, 'url(#metal)') +
            path(rule, RED) + path(spec, '#a0a0a0', (W - sw) / 2, top))
    P = 2; vb = (-PX - P, -PT - P, W + 2 * PX + 2 * P, bottom + PT + 2 * P)
    write('c2-nameplate/amiga-unix-nameplate.svg', svg(vb, body, defs))
    A, _ = L_A()
    def fav(G):
        if G == 16:
            return svg((0, 0, 16, 16), path(rrect(0, 0, 16, 16, 2), '#a8a8a8') + path(box(1, 1, 15, 15), '#161616') +
                       path(pixels(A_WIDE, 2, 2), '#e8e8e8') + path(box(2, 14, 13, 15), RED))
        a = affinity.translate(affinity.scale(A, 20 / 110, 17 / 100, origin=(0, 0)), 6, 5)
        d = ('<linearGradient id="b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ededed"/><stop offset=".5" stop-color="#8a8a8a"/>'
             '<stop offset="1" stop-color="#c4c4c4"/></linearGradient>')
        return svg((0, 0, 32, 32), path(rrect(0, 0, 32, 32, 6), 'url(#b)') + path(rrect(2, 2, 30, 30, 4), '#161616') +
                   path(a, '#000', 0, 1) + path(a, '#e8e8e8') + path(box(6, 25, 26, 27), RED), d)
    return vb, fav

# ---------------------------------------------------------------- concept 3: SVR4 box cover
def c3():
    name, W = oswald('AMIGA UNIX', 100, 0.03)
    spec, sw = oswald(SPEC, 25, 0.34)
    rule = box(0, 0, W, 15); ny = 15 + 24; sy = ny + 100 + 36
    P = 6; vb = (-P, -P, W + 2 * P, sy + 25 + 2 * P)
    for tone, fg, dim in (('dark', '#ffffff', '#8a8a8a'), ('light', '#111111', '#666666')):
        write(f'c3-boxcover/amiga-unix-boxcover-{tone}.svg', svg(vb, path(rule, RED) + path(name, fg, 0, ny) + path(spec, dim, 0, sy)))
    def fav(G):
        if G == 16: return svg((0, 0, 16, 16), path(rrect(0, 0, 16, 16, 2), '#000') + path(box(3, 2, 12, 4), RED) + path(pixels(A_NARROW, 3, 5), '#fff'))
        a, aw = oswald('A', 18); return svg((0, 0, 32, 32), path(rrect(0, 0, 32, 32, 6), '#000') + path(box(6, 4, 26, 8), RED) + path(a, '#fff', (32 - aw) / 2, 10.5))
    return vb, fav

# ---------------------------------------------------------------- rasters, favicons, board
def run(*a): subprocess.run(a, check=True)
def main():
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
    concepts = {'c1-stripes': c1(), 'c2-nameplate': c2(), 'c3-boxcover': c3()}
    rows = []
    for key, (vb, fav) in concepts.items():
        d = os.path.join(OUT, key); svgs = sorted(f for f in os.listdir(d) if f.endswith('.svg'))
        for f in svgs:
            for w, suf in ((None, ''), (2, '@2x')):
                px = round(vb[2] / 2) * (w or 1)          # 1x = caps 50 px tall
                run('rsvg-convert', '-w', str(px), '-o', os.path.join(d, f[:-4] + suf + '.png'), os.path.join(d, f))
        f16, f32 = write(f'{key}/favicon/favicon-16.svg', fav(16)), write(f'{key}/favicon/favicon.svg', fav(32))
        fd = os.path.join(d, 'favicon')
        run('rsvg-convert', '-w', '16', '-o', f'{fd}/favicon-16.png', f16)
        for s in (32, 48, 180, 512):
            run('rsvg-convert', '-w', str(s), '-o', f'{fd}/{"apple-touch-icon" if s == 180 else "icon"}-{s}.png' if s in (180, 512) else f'{fd}/favicon-{s}.png', f32)
        run('magick', f'{fd}/favicon-16.png', f'{fd}/favicon-32.png', f'{fd}/favicon-48.png', f'{fd}/favicon.ico')
        rows.append((key, round(vb[2] / 2), [f for f in svgs]))
    # board
    font = os.path.join(HERE, 'oswald-600-latin.woff2')
    h = [f'<html><head><style>@font-face{{font-family:Oswald;font-weight:600;src:url(file://{font}) format("woff2")}}'
         'body{margin:0;background:#1b1b1b;font-family:Helvetica,Arial,sans-serif;color:#ddd;width:1100px}'
         '.c{margin:0 0 18px}.lab{font:600 15px Oswald;letter-spacing:.1em;color:#fff;background:#333;padding:6px 14px}'
         '.page{background:#000;padding:34px 20px 18px;text-align:center}.page h1{font:600 26px Oswald;letter-spacing:.06em;text-transform:uppercase;color:#fff;margin:14px 0 6px}'
         '.page p{max-width:620px;margin:10px auto 0;text-align:left;font-size:15px;line-height:1.55;color:#d4d4d4}'
         '.lt{background:#f2f0ea;padding:22px;text-align:center}.fav{display:flex;gap:28px;align-items:center;padding:14px 20px;background:#2a2a2a}'
         '.tab{display:flex;align-items:center;gap:8px;padding:6px 12px;border-radius:8px 8px 0 0;font-size:13px}'
         '.big{image-rendering:pixelated;width:128px;height:128px}</style></head><body>']
    for key, w, svgs in rows:
        dark = next(s for s in svgs if 'light' not in s); light = next((s for s in svgs if 'light' in s), dark)
        fd = f'{OUT}/{key}/favicon'
        h.append(f'<div class="c"><div class="lab">{key.upper()} &mdash; header at {w} px (caps 50 px)</div>'
                 f'<div class="page"><img src="file://{OUT}/{key}/{dark}" width="{w}"><h1>Year of the Amiga Unix Desktop 2026</h1>'
                 '<p>Amiga Unix &mdash; Amix &mdash; was Commodore\'s System V Release 4 for the Amiga: shipped in 1990&ndash;92 for the A2500UX and A3000UX, then left where it stood.</p></div>'
                 f'<div class="lt"><img src="file://{OUT}/{key}/{light}" width="{w}"></div>'
                 f'<div class="fav"><div class="tab" style="background:#dee1e6;color:#222"><img src="file://{fd}/favicon-16.png" width="16" height="16">amigaux.org</div>'
                 f'<div class="tab" style="background:#35363a;color:#eee"><img src="file://{fd}/favicon-16.png" width="16" height="16">amigaux.org</div>'
                 f'<img src="file://{fd}/favicon-32.png" width="32"><img class="big" src="file://{fd}/favicon-16.png"><img class="big" src="file://{fd}/favicon-32.png">'
                 f'<img src="file://{fd}/apple-touch-icon-180.png" width="90"></div></div>')
    h.append('</body></html>')
    hp = write('board.html', ''.join(h))
    run('chromium', '--headless', '--disable-gpu', '--allow-file-access-from-files', '--hide-scrollbars',
        '--window-size=1100,2000', f'--screenshot={OUT}/board.png', f'file://{hp}')
    print('done:', OUT)

if __name__ == '__main__':
    main()
