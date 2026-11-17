---
title: "Install: install CD"
---

## Install: install CD

One install CD for every supported machine and both kernel lines, the 68060 and the 68030:
[`amix-1.1.2-install.iso`](../downloads/index.md#media). It installs onto a disk you choose, which is
erased: 1.1 is a clean install. From 1.1 on, later releases upgrade an installed 1.1 system in
place, with its packages through `apkg`: 1.1 is the last release that only installs clean.

### You need

- the install CD, burnt to a disc, or as an image on a CD emulator or on the Z3660's SD card;
- a way to start it, one of:
    - the CD itself, with the drive on an A4091 whose boot ROM carries a CD filesystem (tested in
      emulation). An A4092, or any other controller, does not boot the CD: start from the
      floppies or the Z3660 boot disk, then install from the CD as usual (tested on an A4000 with
      an A4092);
    - the two boot floppies for your line: `amix-1.1.2-boot-k46-1.adf` and `-2.adf` (68040/68060),
      or `amix-1.1.2-boot-k30-1.adf` and `-2.adf` (68030). The machines with the CD on the IDE port,
      the A1200 among them, start this way: Kickstart does not boot an IDE CD;
    - on a Z3660, the boot disk `amix-1.1.2-boot-z3660.hdf` in a preset;
- a target disk on one of the [supported controllers](../hardware/index.md#drivers), of at least
  200 MiB for the standard set or 640 MiB for everything (the smallest disks tested);
- the Kickstart ROM for your machine, from your own ROMs.

The CD drive goes at SCSI id 2 or 3 on the first or second disk controller, at id 5 on any of
the first four, on the IDE port as the slave, or on a Buddha.

### Install

1. Start from the CD, the floppies or the Z3660 boot disk.
2. The installer finds the controllers, the CD and the disks by itself. It shows each disk with
   its controller and what it holds; choose the target by its id. It offers the disk's own size,
   also over an older layout. Then choose the package set: *standard*, the standard Amiga UNIX
   installation, or *x11*, everything on the disc (150.8 MB). The menu shows each set's whole
   size, and a root too small for the set is refused before anything is written, with the root
   size that holds it.
3. When it is done, take out the floppies or the boot disk, and the CD. A boot disk left in place
   can win over the new install: Kickstart boots the bootable partition with the highest
   priority, and the new disk's is 2.
4. Switch off and on. The new system asks its questions once, root's password among them:
   [first boot](../docs/first-boot.md). Root has no password and cannot log in until then.

A disk at the install CD's own address is not offered as a target; any other, SCSI id 5
included, is. (The 1.1 install CD keeps every disk at id 5 out.) It takes an install disc for the
machine's processor line and calls it an "amigaux install disc": a disc that does not fit is
named with its build date and skipped, and when two fitting discs answer, it can list them with
their build dates and ask which. Use the 1.1.2 disc: the installer does not check the version,
and an older 1.1 or 1.1.1 disc would install its own packages, the kernel among them.

On the IDE port of an A1200 or A4000 the installer installs onto the master; the CD may then be
the slave. Tested in emulation (A1200 and A4000), not yet on real hardware. A single drive
on the motherboard's IDE port must be jumpered as master (or sit beside a master): a drive alone as
slave is not found. A CD-ROM alone on the port works, without interrupts.

The installer also installs onto a disk on a Buddha, master or slave on either port, or on a
Catweasel Z-II: [on a Buddha](ide-disk.md#buddha).

<p class="next" markdown="span">[Network install](network.md) · [Install](index.md)</p>
