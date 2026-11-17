# Install demo — web assets and embed

Embedded on the release page on 2026-09-19. The clips are served from `/video/` on the server
(not kept in this repository) and the markup is in the page itself; this file records what was
chosen and why.

## Files

| File | Size | Runs | What it is |
|------|------|------|------------|
| `install.webm` / `.mp4` | 839 K / 461 K | 41 s | Install: boot → 68060 banner → the whole interview → confirmation |
| `first-boot.webm` / `.mp4` | 5.6 M / 4.4 M | 68 s | First boot: banner → firstboot dialog → summary → `amix login:` |
| `install-full.webm` / `.mp4` | 6.3 M / 4.8 M | 109 s | Both, back to back — deployed but NOT embedded; there if the page ever wants one hero clip |
| `*.gif` | 36–57 K | 10 s | Fallback for no-`<video>` clients; first 10 s only |
| `*.png` | 72–171 K | — | Poster frames |

Durations are after the 2026-09-19 edit: 16 s of dead hold removed from each clip
(install 00:02–00:18, first-boot 00:04.7–00:20.7 — the same two stretches as 00:02–00:18 and
01:02–01:18 of the combined file, mapped back to the per-clip timelines by measuring the
57.267 s concat offset). Both cuts land inside a static hold and the frames either
side are pixel-identical, so the joins are invisible; each screen still dwells 3.5–4.5 s.

All video is 1440×1136 (the 720×568 Amiga display at an integer 2×, nearest-neighbour). Draw it at
half that in CSS and it stays pixel-crisp on HiDPI screens.

## What is on the page, and why

Two clips, not the combined one, placed immediately after the "Soon: install it yourself"
callout — that section makes the claim ("comes down to following the prompts") and these are the
evidence for it, so they sit under the sentence they prove rather than in a gallery.

The install clip autoplays muted and loops: at 41 s it is short enough to loop without the restart
feeling random, and it is the one that carries the claim. First boot is click-to-play with a
poster and `preload="none"` — only one thing moves on the page, nobody downloads 4 MB they did not
ask for, and the two together still read in order.

Two behaviours worth keeping if this markup is reused: `prefers-reduced-motion: reduce` turns the
autoplay off and gives that visitor controls instead; and if a browser *refuses* autoplay (data
saver, low power mode, a per-site setting) the script gives controls too — without that, a refused
autoplay leaves the visitor at a static poster with no way to start it.

## Markup — as embedded

```html
<figure class="demo">
  <video id="demo-install" autoplay muted loop playsinline preload="metadata"
         poster="/video/install.png" width="1440" height="1136">
    <source src="/video/install.webm" type="video/webm">
    <source src="/video/install.mp4"  type="video/mp4">
    <img src="/video/install.gif" alt="Installing Amiga Unix on a 68060: the installer asks for keymap, disk, sizes and package set, then summarises what it will install.">
  </video>
  <figcaption><b>Installing on a real 68060.</b> Keymap, disk, partition sizes, package set — then
  it shows you what it is about to do. Real time, with the long waits taken out.</figcaption>
</figure>

<figure class="demo">
  <video controls muted playsinline preload="none"
         poster="/video/first-boot.png" width="1440" height="1136">
    <source src="/video/first-boot.webm" type="video/webm">
    <source src="/video/first-boot.mp4"  type="video/mp4">
    <img src="/video/first-boot.gif" alt="First boot: Amiga Unix asks for a nodename and domain, writes its hosts file and comes up at a login prompt.">
  </video>
  <figcaption><b>First boot.</b> It names itself, sets the clock, writes its hosts file — including
  the package repository — and comes up at a login prompt.</figcaption>
</figure>
```

```css
.demo { margin: 1.75rem 0 0; }
.demo video {
  display: block; width: 100%; max-width: 720px; height: auto;
  aspect-ratio: 1440 / 1136;           /* hold the box before it loads */
  background: #000; border: 1px solid var(--rule);
  image-rendering: pixelated;          /* never smooth a pixel display */
}
.demo img { display: block; width: 100%; max-width: 720px; height: auto; image-rendering: pixelated; }
.demo figcaption { margin-top: 0.5rem; color: var(--dim); font-size: 0.85rem; line-height: 1.5; }
.demo figcaption b { color: var(--fg); font-weight: 400; }
```

Plus the small script at the end of the page that handles reduced-motion and refused autoplay —
see "What is on the page, and why" above.

## Provenance

Cut from a screen capture of an install, with the static holds compressed: the interview is
about 85% frozen screen, so the dead holds are sped up and the typing is left alone. Lossless
masters are kept with the capture, so a re-cut never needs a re-capture.

Every frame of all three clips and all five posters was OCR-scanned before publishing. The
values on screen are the node name `amix`, the domain `amigaux.org`, the repository
`pkg.amigaux.org` with its public address, and a private example address for the host.

**One editorial consequence worth knowing:** the install clip ends on the confirmation summary
rather than on "installation begins". The installer's debug output is already on screen from
about 267 s, so the cut was pulled back to 267.0 s. To end on the "installation begins" beat
instead, the capture needs re-doing with that output suppressed.
