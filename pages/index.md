## Amiga UNIX, again

Amigaux.org is a compilation of hobby projects trying to make Commodore's original Amiga UNIX
more easily accessible, and to get it running on newer Amiga hardware.

Amiga Unix was Commodore's System V Release 4 for the Amiga. It was notoriously picky on
hardware and was basically only installable on the original hardware it was shipped on: the
A2500UX and A3000UX.

What that means today: a 68040/68060 port, native drivers for the Z3660 and the A4091/A4092, an
installer that does the whole job, and a package repository with modern GNU tools.

<section class="note" markdown>

### amigaux 1.1.2

1.1 with the MNT VA2000 and ZZ9000 graphics cards and updated packages, which an installed 1.1 or
1.1.1 takes through `apkg upgrade`; the ZZ9000 is tested in emulation, the VA2000 not yet on a real
card. The install media are 1.1.2's: ready-installed disk images for the Z3660, the A3000, the IDE
port and a Buddha, one install CD for every supported machine, and a network install. Drivers load
as modules; SSH is on from the first boot. Released %DATE_1_1_2%.

[Install](install/index.md) · [Downloads](downloads/index.md) · [Release notes](release-notes/1.1.2.md)

</section>

## Latest

<ul class="news">
  <li><time>%DATE_1_1_2%</time>amigaux 1.1.2: the MNT VA2000 and ZZ9000 graphics cards, X-Surf link reporting and updated packages, through <code>apkg upgrade</code>. <a href="release-notes/1.1.2/">Release notes</a>.</li>
  <li><time>%DATE_1_1_1%</time>amigaux 1.1.1 released: the Buddha and Catweasel Z-II IDE and the X-Surf Ethernet, ready-made images for a Buddha. <a href="release-notes/1.1.1/">Release notes</a>, <a href="downloads/">downloads</a>.</li>
  <li><time>2026-11-10</time>amigaux 1.1 released: <a href="release-notes/1.1/">release notes</a>, <a href="downloads/">downloads</a>.</li>
</ul>

[All news](news/index.md)

<div class="tiles">
  <a href="install/"><b>Install</b><span>Pick your machine and medium; one page per route.</span></a>
  <a href="downloads/"><b>Downloads</b><span>Every file with its size, and one SHA256SUMS to check them.</span></a>
  <a href="hardware/"><b>Hardware</b><span>What runs 1.1, and what is tested where.</span></a>
</div>
