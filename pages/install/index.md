## Install

amigaux 1.1.2: Amiga UNIX (Amix) 2.1 as ready-installed disk images, for the Z3660, the A3000,
the IDE port of an A1200 or A4000 and a Buddha, and an install CD and a network install for every
supported machine. Pick your row. A system installed from 1.1 or 1.1.1 takes 1.1.2 in place
through `apkg`: [upgrading](../release-notes/1.1.2.md#upgrade).

<div class="tbl" markdown>

| Machine | Image | Route |
|---|---|---|
| A3000, A4000 or A4000T with a Z3660 and a real 68060 or 68LC060 | 68060 image | [Z3660 SD card](z3660-sd.md) — the main route<br>[the SD card kit](../downloads/index.md#kit) or [the image](../downloads/index.md#k46) |
| A3000, the disk at SCSI id 6 on its own controller | 68030 image | [68030 disk](68030-disk.md) — tested in emulation only<br>[the image](../downloads/index.md#k30) |
| A1200 or A4000, the system on a CF or SD card as the master on its own IDE port | IDE image | [IDE disk](ide-disk.md) — tested in emulation only<br>[the images](../downloads/index.md#ide) |
| A2000, A3000 or A4000 with a Buddha, the system as the master on its first port | Buddha image | [On a Buddha](ide-disk.md#buddha) — tested in emulation only<br>[the images](../downloads/index.md#buddha) |
| A1200 with a 68030, 68040 or 68060 card with an MMU and fast memory below 1 GiB; the system on its own IDE port | install CD | [Install CD](cd.md) on the IDE slave, started from the boot floppies — tested in emulation. The network install only with an A2065 on a Zorro busboard, untested |
| Any [supported machine](../hardware/index.md), onto a disk you choose: an A4000 with a full 68030 (MMU) card and an A4091 or A4092, the A4000T's onboard SCSI, the A4000's IDE port | install CD | [Install CD](cd.md), started from two floppies or a Z3660 boot disk, or by itself through an A4091 boot ROM that carries a CD filesystem |
| The same, over the network | network install | [Network install](network.md) |
| An emulator | either image | [Emulator](emulator.md) |

</div>

**1.1 is a clean install.** It replaces a 1.0 system; nothing is carried over. Coming from 1.0:
[back up first](from-1.0.md). From 1.1 on, later releases upgrade an installed 1.1 system in
place, with its packages through `apkg`: 1.1 is the last release that only installs clean.

**Every route:** bring your own Kickstart ROM image; we ship none.

**The A4000T's onboard SCSI** is an install target on the 68060 line (tested in emulation), not
with the Z3660 in 68030 mode: use the [install CD](cd.md).

**Installing onto the IDE port** of an A1200 or A4000, the master only (a CF card as slave is often
unstable on Amigas): tested in emulation (A1200 and A4000), not yet on real hardware.

**Not supported:** the stock A4000's 68EC030 (no MMU), any 68000/68020 Amiga. The A600 is
planned.

After the install the system asks its questions once: [first boot](../docs/first-boot.md).

Stuck? Report it in [%SUPPORT_REPO%](%SUPPORT_ISSUES%); see [Support](../about/index.md#support).
