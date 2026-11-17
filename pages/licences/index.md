---
title: "Licences"
---

## Licences

Every piece of software amigaux ships keeps its own licence. The full texts are on the installed
system; this page lists what the licences ask us to say, and where to find them.

### Where the licences are

- A package's licences: `/opt/amix/doc/<package>/`.
- A kernel or driver package's: `/var/sadm/pkg/<package>/install/copyright`.

### Acknowledgements

These licences ask that anything advertising the software's features or use carries their line.

**The floating-point emulation in the 68040/68060 kernel** (`kern46m`):

- This product includes software developed by Gordon Ross
- This product includes software developed by the University of California, Lawrence Berkeley
  Laboratory.

Licence: `/var/sadm/pkg/kern46m/install/copyright`.

**Heirloom tar**, the system's `/usr/sbin/tar` (`heirtar`):

- This product includes software developed or owned by Caldera International, Inc.

Licence: `/opt/amix/doc/heirloom-tar/LICENSE`.

**rdate**, which sets the clock from time servers:

- This product includes software developed by Christos Zoulas.

Licence: `/opt/amix/doc/rdate/LICENSE`.

**prngd**, the entropy daemon:

- This product includes software developed by the University of California, Berkeley and its
  contributors.

Licence: `/opt/amix/doc/prngd/LICENSE`.

### Copyright notices

Code under these notices is built into the system.

**Motorola's floating-point and integer support packages**, in modified versions, in the
68040/68060 kernel. Motorola's notice in full is linked into every such kernel and is in
`/var/sadm/pkg/kern46m/install/copyright`.

- M68040 Software Package Copyright (c) 1993, 1994 Motorola Inc. All rights reserved.
- M68060 Software Package Copyright (C) 1993, 1994, 1995, 1996 Motorola Inc. All rights reserved.

**The CD filesystem**, `cdfs`, from Stefan Reinauer's ODFileSystem. Licence:
`/var/sadm/pkg/cdfs46/install/copyright` (`cdfs30` on a 68030).

- Copyright (c) 2026 Stefan Reinauer

**The SCSI SCRIPTS in the A4091/A4092 and A4000T drivers**, made with Michael L. Hitch's NCR
53C710 assembler from NetBSD. Notice: `/var/sadm/pkg/a409146/install/copyright` (`a409130` on a
68030; `a4kt71046` and `a4kt71030` for the A4000T), and in the 68030 kernel's,
`/var/sadm/pkg/kern30m/install/copyright`.

- Copyright (c) 1995,1999 Michael L. Hitch

### Source code

The ZZ9000 service modules (`zz9ksvc30`, `zz9ksvc46`) are under the GPL, version 3 or later, as
they carry the ZZ9000 SDK's headers. Their source is
[`kernel/modules/zz9ksvc`](%GITHUB_ORG%/amix/tree/master/kernel/modules/zz9ksvc) in amix; their
licence is in `/var/sadm/pkg/zz9ksvc46/install/copyright`.

The Z3660 firmware, the release's [firmware file](../downloads/index.md#z3660) and the
[SD card kit](../downloads/index.md#kit)'s `fat/`, is built from the Z3660 source, under the GPL,
version 3: `Z3660.bin` from
[`amix-1.1`](https://github.com/jusii/Z3660-amix/tree/amix-1.1) of our fork, `BOOT.BIN` and
`FAILSAFE.bin` as upstream's, [shanshe/Z3660](https://github.com/shanshe/Z3660). It holds
third-party parts under their own licences: the Xilinx standalone BSP and FSBL, lwIP (BSD),
mbedTLS (Apache-2.0) and the UAE CPU core (GPL-2). The kit's CPLD file, boot screen and timings
come from the Z3660 project, under the GPL, version 3.

### With thanks

These authors ask for credit without making it a condition:

- Jean-loup Gailly and Mark Adler, for zlib;
- Julian Seward, for bzip2;
- the SQLite authors (SQLite comes with Python);
- Lutz Jaenicke, for prngd.

The Z3660 Ethernet driver's STREAMS skeleton descends from Commodore's Amix `aen.c` by Keith
Gabryelski, by way of Ignacio Soriano's hydra-amix driver.

<p class="next" markdown="span">[About](../about/index.md)</p>
