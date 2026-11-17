---
title: "Install: network install"
---

## Install: network install

The network install starts a small system from a RAM disk and takes the packages from
`http://pkg.amigaux.org/1.1`. It runs in two stages: first a minimal system onto the target
disk, then, at its first boot, the rest of the package set you chose, from the repository. A
broken download is tried again, and an interrupted second stage carries on where it stopped.

### You need

- a network card the system drives (the Z3660's Ethernet, an A2065, or an X-Surf-100 or X-Surf:
  [their interface names](../docs/networking.md#interfaces)) and a network that reaches the internet,
  with a fixed address for the machine: the installer takes no DHCP. The installed system's first
  boot offers DHCP or a fixed address. Installing over an X-Surf is tested in emulation only: with
  a Z3660 (68060) and an X-Surf-100 in Zorro III, and on an A3000 with a 68030 and an X-Surf in
  Zorro II;
- the network-install CD, [`amix-1.1.2-netinstall.iso`](../downloads/index.md#media). It starts like
  the [install CD](cd.md): with the boot floppies or the Z3660 boot disk, or by itself through an
  A4091 boot ROM that carries a CD filesystem;
- a target disk on a supported controller, which is erased. The full set needs 1 GiB; on a
  512 MiB disk the installer warns and lets you choose a smaller set;
- the Kickstart ROM for your machine, from your own ROMs.

### Install

1. Start the network-install CD as you would the install CD.
2. Give the network settings (the interface, the address, the netmask, and the gateway and name
   server if there are any), choose the target disk by its id, and choose the package set:
   *minimal*, *standard* or *full*.
3. The first stage puts a minimal system on the disk: the base packages, the kernel and its
   modules. If the repository lacks a package of the set you chose, it stops here, before
   installing anything.
4. Take out the boot floppies or boot disk and the CD, and switch off and on. A boot disk left in
   place starts again: its priority, 5, is above the installed disk's 2.
5. At the first boot the system asks its questions once ([first boot](../docs/first-boot.md)),
   with the network answers you gave as the defaults. Then, before the login prompt, it fetches
   the rest of the set, one package at a time with a line for each, trying each three times.
   With the full set this first boot can take over an hour (65 minutes to the login prompt,
   measured over the internet); the standard set takes much less. Let it run.

If the network drops during that first boot, each package is tried three times, 30 seconds apart,
and a stalled download waits up to 5 minutes for data on each try, so one package can hold the
boot for about three quarters of an hour. If it still does not install, the first boot says what
is missing and goes on to the login prompt; the system works with what it has, and the next boot
carries on (or, as root, `/sbin/sh /var/adm/firstboot/netset.sh`). If the repository no longer
has a package the installation chose, it stops at once and says so.

On a Z3660 the [SD card kit](z3660-sd.md#kit) has it ready, with no CD at all: its preset 2 starts
the network installer from the card, with an empty 1 GiB disk at unit 6 to install onto; preset 3
then boots that disk.

<p class="next" markdown="span">[Install CD](cd.md) · [Install](index.md)</p>
