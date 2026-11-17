## Downloads

<p class="rc" markdown="span">**amigaux 1.1.2**, its install media released %DATE_MEDIA_1_1_2%: the
[release on GitHub](https://github.com/amigaux/amix-media/releases/tag/1.1.2).
Tested in emulation only: the installer in seven set-ups (the install CD on a Z3660 with a 68060
and on an A3000 with a 68030; the boot floppies with the CD onto an IDE disk, on both lines; the
Z3660 boot disk; the network install with the full set, on both lines) and each of the six
ready-made images, every one passing all ten of its checks. The VA2000 and ZZ9000 drivers are not
yet tested on real cards.</p>

The 1.1.2 files replace the 1.1.1 files. A system already installed from 1.1 or 1.1.1 does not need
them: it takes 1.1.2 in place through `apkg` ([upgrading](../release-notes/1.1.2.md#upgrade)).

amigaux 1.1 is a clean install: it replaces a 1.0 system, it does not upgrade it. Coming from 1.0?
Read [Coming from 1.0](../install/from-1.0.md) first. From 1.1 on, later releases upgrade an
installed 1.1 system in place, with its packages through `apkg`: 1.1 is the last release that only
installs clean.

Bring your own Kickstart ROM image; none is included. Checksums for every file:
[`SHA256SUMS`](%MEDIA_1_1_2%/SHA256SUMS), and [how to check them](verify.md).

### Disk images {#images}

Each image is a whole system, installed and ready for its first boot: the Amix disk only, with
no Z3660 firmware and no AmigaOS. It comes as a zip file holding one `.img` file: 3600 MiB
(3,774,873,600 bytes), or 1800 MiB (1,887,436,800 bytes) for an IDE or Buddha image. Each boots in one place only; every other machine and controller installs
from the [install CD](#media), which lays a disk wherever you choose.

<div class="tbl dl" markdown>

| File | What | Size |
|---|---|---|
| <span id="k46"></span>[`amix-1.1.2-k46-4g.zip`](%MEDIA_1_1_2%/amix-1.1.2-k46-4g.zip) | 68060 image — A3000, A4000 or A4000T with a Z3660 and a real 68060 or 68LC060; boots from the Z3660's SCSI unit 6; tested in emulation only, with a Z3660 | <span class="num">93.1 MB</span> |
| <span id="k30"></span>[`amix-1.1.2-k30-4g.zip`](%MEDIA_1_1_2%/amix-1.1.2-k30-4g.zip) | 68030 image — an A3000, the disk at SCSI id 6 on its own controller; tested in emulation only, on an A3000 with an A4091 fitted | <span class="num">92.9 MB</span> |
| <span id="ide"></span>[`amix-1.1.2-k46-ide-2g.zip`](%MEDIA_1_1_2%/amix-1.1.2-k46-ide-2g.zip) | IDE image, 68040/68060 — the IDE master of an A1200 or A4000, on a CF or SD card of 2 GB or more; tested in emulation only, on an A4000 with a Z3660 | <span class="num">87.6 MB</span> |
| [`amix-1.1.2-k30-ide-2g.zip`](%MEDIA_1_1_2%/amix-1.1.2-k30-ide-2g.zip) | IDE image, 68030 — the same, with a 68030; tested in emulation only, on an A4000 with a 68030 | <span class="num">87.3 MB</span> |
| <span id="buddha"></span>[`amix-1.1.2-k46-buddha-2g.zip`](%MEDIA_1_1_2%/amix-1.1.2-k46-buddha-2g.zip) | Buddha image, 68040/68060 — the master on the first port of a Buddha, on a CF or SD card or a disk of 2 GB or more; tested in emulation only, the Buddha beside a Z3660: [on a Buddha](../install/ide-disk.md#buddha) | <span class="num">87.7 MB</span> |
| [`amix-1.1.2-k30-buddha-2g.zip`](%MEDIA_1_1_2%/amix-1.1.2-k30-buddha-2g.zip) | Buddha image, 68030 — the same, with a 68030; tested in emulation only, the Buddha alone | <span class="num">87.5 MB</span> |

</div>

Next: [write the image](write-image.md), then [install](../install/index.md).

### Z3660 SD card kit {#kit}

Everything a Z3660's microSD card needs for 1.1.2, in two folders, one per partition: the firmware
CDEB9618 with upstream's stock start-up loader, the settings and presets, and the disks: the ready
installed 68060 system (the same as the 68060 image), the Z3660 boot disk, the network installer
and an empty 1 GiB disk. No Kickstart ROM. Three of the Z3660 project's own files come from
upstream: [Z3660 SD card](../install/z3660-sd.md#kit).

<div class="tbl dl" markdown>

| File | What | Size |
|---|---|---|
| [`amix-1.1.2-z3660-sd-kit.zip`](%MEDIA_1_1_2%/amix-1.1.2-z3660-sd-kit.zip) | Z3660 SD card kit — a microSD card of 8 GB or more; its files take 4.9 GB unpacked | <span class="num">109.1 MB</span> |

</div>

The firmware files in it are built from the Z3660 source (GPL-3), with third-party parts under
their own licences: the Xilinx standalone BSP and FSBL, lwIP (BSD), mbedTLS (Apache-2.0) and the
UAE CPU core (GPL-2). The CPLD file, the boot screen and the timings come from the Z3660 project
(GPL-3).

### What is on an image {#layout}

<div class="tbl" markdown>

| Slice | What | Size |
|---|---|---|
| 1 | root, `ufs` | <span class="num">2047 MiB</span> |
| 2 | swap | <span class="num">64 MiB</span> |
| 3 | boot store: the kernels and modules the system boots | <span class="num">64 MiB</span> |
| 4 | `/home`, `ufs` | <span class="num">1424 MiB</span> |

</div>

Both images carry the *x11* package set: the standard set plus the extras, with the OPEN LOOK
desktop. A file system holds at most 2047 MiB, so a larger disk does not give a larger root.

### Install media {#media}

One install CD for every machine and both lines, and three ways to start it:
[Install CD](../install/cd.md).

<div class="tbl dl" markdown>

| File | What | Size |
|---|---|---|
| [`amix-1.1.2-install.iso`](%MEDIA_1_1_2%/amix-1.1.2-install.iso) | Install CD — every supported machine, the A1200 among them; the 68060 and the 68030 line | <span class="num">131.1 MB</span> |
| [`amix-1.1.2-netinstall.iso`](%MEDIA_1_1_2%/amix-1.1.2-netinstall.iso) | Network-install CD — starts like the install CD, takes the packages from the repository | <span class="num">16.5 MB</span> |
| [`amix-1.1.2-boot-k46-1.adf`](%MEDIA_1_1_2%/amix-1.1.2-boot-k46-1.adf) | Boot floppy 1, 68040/68060 — starts the install CD | <span class="num">880 KB</span> |
| [`amix-1.1.2-boot-k46-2.adf`](%MEDIA_1_1_2%/amix-1.1.2-boot-k46-2.adf) | Boot floppy 2, 68040/68060 | <span class="num">880 KB</span> |
| [`amix-1.1.2-boot-k30-1.adf`](%MEDIA_1_1_2%/amix-1.1.2-boot-k30-1.adf) | Boot floppy 1, 68030 line — starts the install CD | <span class="num">880 KB</span> |
| [`amix-1.1.2-boot-k30-2.adf`](%MEDIA_1_1_2%/amix-1.1.2-boot-k30-2.adf) | Boot floppy 2, 68030 line | <span class="num">880 KB</span> |
| [`amix-1.1.2-boot-z3660.hdf`](%MEDIA_1_1_2%/amix-1.1.2-boot-z3660.hdf) | Z3660 boot disk — starts the install CD from the Z3660's SD card | <span class="num">14.0 MB</span> |

</div>

These are plain files; `SHA256SUMS` lists them all. The
network install: [Network install](../install/network.md).

### Z3660 firmware {#z3660}

We recommend Z3660 firmware CDEB9618, unchanged from 1.1; 1.1.2 also runs on the stock firmware,
1.03 BETA 21, without its fixes. Its source is the branch
[`amix-1.1`](https://github.com/jusii/Z3660-amix/tree/amix-1.1) of the firmware's repository. What
it fixes, and putting it on the card: [Z3660 SD card](../install/z3660-sd.md#firmware).

<div class="tbl dl" markdown>

| File | What | Size |
|---|---|---|
| [`z3660-firmware-1.1-CDEB9618.bin`](%MEDIA_1_1_2%/z3660-firmware-1.1-CDEB9618.bin) | Z3660 firmware, CRC32 `CDEB9618`: goes on the card as `Z3660.bin` | <span class="num">12.8 MB</span> |
| [`z3660-firmware-1.1-README.txt`](%MEDIA_1_1_2%/z3660-firmware-1.1-README.txt) | What the firmware changes, how to install it and go back | <span class="num">2.6 KB</span> |

</div>

The 1.1.1 files stay on [GitHub](https://github.com/amigaux/amix-media/releases/tag/1.1.1), and the
1.1 files [too](https://github.com/amigaux/amix-media/releases/tag/1.1). The 1.0 files stay at [`/files/1.0/`](https://amigaux.org/files/1.0/SHA256SUMS).
