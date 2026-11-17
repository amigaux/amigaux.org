---
title: "Install: IDE disk"
---

## Install: IDE disk

An A1200 or an A4000, with the system on a CF or SD card as the master on the machine's own IDE
port. Two images, one for each line: `amix-1.1.2-k46-ide-2g` for a 68040 or 68060,
`amix-1.1.2-k30-ide-2g` for a 68030.

<span class="tier t-emu">Supported · emulation</span> Tested in emulation only:

- the 68040/68060 image on an A4000 with a Z3660;
- the 68030 image on an A4000 with a 68030.

1.1's IDE images, the same system without the two new drivers, also ran in emulation on an A1200,
with a DKB 1240 (68040) and with a Blizzard 1230-III (68030).

Each carries the *x11* package set, X11R6.3 included: the standard set plus the extras, with the
OPEN LOOK desktop. On the disk: the root (1671 MiB), swap (64 MiB) and the boot store (64 MiB).

### You need

- the [IDE image](../downloads/index.md#ide) for your processor, unzipped: 1800 MiB;
- a CF or SD card of 2 GB or more, with an adapter for the IDE port;
- on an A1200, an accelerator with an MMU and its fast memory below 1 GiB; with memory above it,
  as on a Blizzard 1260, the boot loader stops with `no fast memory below 0x40000000`;
- on an A4000, a 68040 or 68060 card (tested: the Z3660; the A3640 is untested) or a full 68030
  card with an MMU: not the stock A4000/030 card, a 68EC030 with no MMU
  ([hardware](../hardware/index.md));
- the Kickstart ROM for your machine, from your own ROMs.

### Install

1. On a PC, [write the image](../downloads/write-image.md#ide) to the card.
2. Put the card on the IDE port as the master. A CF card works as the master only. A single
   drive on the motherboard's IDE port must be jumpered as master: a drive alone as slave is not
   found.
3. Power on. Kickstart boots the card by itself and the system asks its questions once:
   [first boot](../docs/first-boot.md). Then log in as `root` with the password you gave it.
   Its boot partition has priority 2: it wins over an AmigaOS disk at 0, but a disk above 2, such
   as an older Amix install, wins over it.

**AmigaOS starts instead:** hold both mouse buttons at power-on, Boot Options, `UNIX_Boot`.

**The images are for the motherboard's IDE port,** not for an add-on IDE card such as a Buddha,
which has images of its own: [on a Buddha](#buddha). A system already installed on the
motherboard's port moves to a Buddha with one rebuild that names the new controller:
[moving the system disk](../hardware/index.md#moving-disk).

Another disk, or a disk behind another controller: use the [install CD](cd.md), which sets up the
disk for the controller it is on.

Stuck? Report it in [%SUPPORT_REPO%](%SUPPORT_ISSUES%); see [Support](../about/index.md#support).

### On a Buddha {#buddha}

From [1.1.1](../release-notes/1.1.1.md): a ready-made image for the master on the first port of an
Individual Computers Buddha, one for each line: `amix-1.1.2-k46-buddha-2g` for a 68040 or 68060,
`amix-1.1.2-k30-buddha-2g` for a 68030.

<span class="tier t-emu">Supported · emulation</span> Tested in emulation only: the 68040/68060
image with the Buddha beside a Z3660, the 68030 image with the Buddha alone.

Each carries the *x11* package set and both 1.1.1 drivers. On the disk, as on the IDE images: the
root (1671 MiB), swap (64 MiB) and the boot store (64 MiB).

You need:

- the [Buddha image](../downloads/index.md#buddha) for your processor, unzipped: 1800 MiB;
- a disk, or a CF or SD card, of 2 GB or more, with an adapter for the Buddha's IDE port;
- the Buddha in a Zorro slot: an A2000, A3000 or A4000 with a 68030 for the 68030 image, with a
  68040 or 68060 for the other (an A4000 with a Z3660, for example);
- the processor and memory as for the IDE images above;
- the Kickstart ROM for your machine, from your own ROMs.

Install:

1. On a PC, [write the image](../downloads/write-image.md#ide) to the disk, as for the IDE
   images.
2. Put the disk on the Buddha's first port as the master. The system finds its disk by the
   card's identity and the drive's unit, wherever Kickstart placed the card and whatever other
   controllers the machine has.
3. Power on. The machine boots from the disk through the Buddha's own ROM, the kernel then drives
   the card, and the system asks its questions once: [first boot](../docs/first-boot.md).
   Its boot partition has priority 2, as on the IDE images: it wins over an AmigaOS disk at 0, but
   a disk above 2 wins over it. To change which one boots, change the other disk's priority in
   HDToolBox, or this one's.

On another position, the first port's slave or the second port, the disk boots once its boot
generation names that unit: from a boot that mounts its root, rebuild it as in
[moving the system disk](../hardware/index.md#moving-disk), with the new unit. The Buddha's units
are fixed: port 0's master is 6 and its slave 5, port 1's master 3 and its slave 2.

**From the install CD.** The [install CD](cd.md), from 1.1.1 on, also installs onto a disk on a Buddha,
master or slave on either port: the installer lists its disks as "Buddha IDE", and the CD drive
can be on the Buddha too. The boot floppies and the Z3660 boot disk start the installer with the
Buddha's driver loaded. The new system's boot generation names the card by its identity and the
disk's unit, so the disk boots wherever Kickstart placed the card.
<span class="tier t-emu">Supported · emulation</span> Tested in emulation only, on both lines, with a
development build of the same installer, kernels and driver: installing onto the first port's
master and onto a lone slave on the first port, each then booted from the Buddha, with the CD
drive on an A4091 or as the slave on the motherboard's IDE port; and, with the CD drive on the
Buddha itself (its second port's master), installing onto the master on the motherboard's IDE
port. The installer offers the second port as a target too; that is not yet tested.

The install CD and the network installer offer a Catweasel Z-II's disks the same way, as
"Catweasel Z-II IDE" (tested in emulation on both lines).

<p class="next" markdown="span">[First boot](../docs/first-boot.md) · [Packages](../packages/index.md) · [Known issues](../docs/known-issues.md)</p>
