AMIGA UNIX — period logo concepts for amigaux.org   (2026-09-17)
=================================================================
NOT demo assets: the granite AMIX / AMIGA UNIX emblem stays in the Saku demo.

Brief
  - Original shapes only: no Commodore C=, no Amiga tick, no Boing ball.
  - Wordmark AMIGA UNIX on one line, with "68040 · 68060" small and letter-spaced under it.
  - Built for the current site: black page, Oswald SemiBold headline. Light versions are extras.
  - White/silver only; ONE red rule is the single accent (#d62d2d).
  - Favicon = a single A in the concept's style + the red rule; touch icons use the same mark.

Concepts
  c1-stripes/    1990 workstation scan-line lettering. Hand-built extended caps cut into 8 bars;
                 the red rule is the 9th bar, on the same rhythm.
  c2-nameplate/  A3000UX-style case badge: the same caps in brushed metal on a dark bezelled plate.
                 One file only; the plate carries its own ground, so it works on black and light.
  c3-boxcover/   1991 software box / SVR4 manual cover: Oswald SemiBold (the page's own face)
                 under a heavy red rule, spec line flush left.
  board.png      all three in a mock of the site header, the light versions, and the favicons on
                 light/dark browser tabs (real size + 8x zoom).

Files per concept
  amiga-unix-*.svg          master artwork. All type is converted to outlines, so there is no font dependency.
  amiga-unix-*.png / @2x    raster at the header size below (1x) and 2x.
  favicon/favicon.ico       16 + 32 + 48. The 16 px layer is HAND-SET pixel art, crisp on the grid.
  favicon/favicon.svg       32-grid vector; favicon-16.svg is the pixel-set 16 px master.
  favicon/favicon-{16,32,48}.png, apple-touch-icon-180.png, icon-512.png

Header size (1x = capitals 50 px tall; the granite emblem is currently 520 px wide)
  c1  <img src="/img/amiga-unix-stripes-dark.svg"   width="484" height="84"  alt="Amiga Unix">
  c2  <img src="/img/amiga-unix-nameplate.svg"      width="528" height="119" alt="Amiga Unix">
  c3  <img src="/img/amiga-unix-boxcover-dark.svg"  width="318" height="107" alt="Amiga Unix">
  In the page's <header>, the <picture> is capped at min(100%, 520px); c1/c2 fit that, and c3 wants
  the cap lowered to its own width or it scales up.

Favicon markup (list the .ico first; an SVG icon would be rendered soft at 16 px)
  <link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
  <link rel="apple-touch-icon" href="/apple-touch-icon-180.png">

Provenance
  Drawn as code (geometry in Python/shapely), not by an image generator: src/gen.py regenerates
  everything (needs shapely, fonttools, brotli, rsvg-convert, ImageMagick, chromium, and
  oswald-600-latin.woff2 beside it — the copy in theme/font/). Oswald is SIL OFL 1.1;
  outlining its glyphs into artwork is permitted.
