## Supported hardware

An MMU is required: the stock A4000's 68EC030 and the 68000/68020 Amigas cannot run Amiga UNIX.

Labels: <span class="tier t-hw">Supported · hardware</span> tested on real machines;
<span class="tier t-emu">Supported · emulation</span> tested in an emulator only;
<span class="tier t-next">Planned</span> not in this release.

### The 68060 line

The 68060 image is for a Z3660: it boots from the Z3660's SCSI unit 6. Every other setup installs
from the [install CD](../install/cd.md).

Z3660 firmware: we recommend CDEB9618, from the 1.1 release; 1.1 also runs on the stock 1.03 BETA
21 (tested on an A4000T with a real 68060), without its fixes:
[Z3660 SD card](../install/z3660-sd.md#firmware).

<div class="tbl" markdown>

| Setup | Status | Notes |
|---|---|---|
| A4000 + Z3660, 68LC060 | <span class="tier t-hw">Supported · hardware</span> | the kernel before the release one (68060-261106-65); the release kernel's one change, to the sound driver, in emulation |
| A4000 + Z3660, full 68060 | <span class="tier t-emu">Supported · emulation</span> | |
| A4000T + Z3660, real 68060 | <span class="tier t-hw">Supported · hardware</span> | the 68060 image on the release kernel: first boot, multi-user, packages from the repository, SSH and telnet logins, a clean halt (Kickstart 47.115, firmware CDEB9618) |
| A3000 + Z3660, real 68060 | untested on 1.1 | 1.0 ran on this hardware |
| A3000 or A4000 with a 68040 card | untested on 1.1 | the 68060 kernel runs on a 68040: tested on the A1200 (below) |

</div>

### The 68030 line

The 68030 image is for the A3000: it boots from SCSI id 6 on the A3000's own controller. Every
other setup installs from the [install CD](../install/cd.md).

<div class="tbl" markdown>

| Setup | Status | Notes |
|---|---|---|
| A3000, the disk on its own SCSI | <span class="tier t-emu">Supported · emulation</span> | |
| A4000 with a full 68030 (MMU) card and an A4091 | <span class="tier t-emu">Supported · emulation</span> | A4091 ROM 40.13 |
| The Z3660 in 68030 mode | <span class="tier t-emu">Supported · emulation</span> | the 68030 kernel with its system on the Z3660, from the install CD; the 68030 image does not boot there |

</div>

### The A1200

<div class="tbl" markdown>

| Setup | Status | Notes |
|---|---|---|
| A1200 with a 68030 accelerator (with an MMU) | <span class="tier t-emu">Supported · emulation</span> | the 68030 line; tested: Blizzard 1230-III, 32 MB |
| A1200 with a 68040 accelerator | <span class="tier t-emu">Supported · emulation</span> | the 68060 line's kernel; tested: DKB 1240, 64 MB |
| A1200 with a 68060 accelerator | untested | a card whose fast memory sits below 1 GiB |
| Blizzard 1230-IV, 1240, 1260 | not yet | the 1260's memory sits above 1 GiB |
| A600 | <span class="tier t-next">Planned</span> | the boot loader cannot yet tell it from an A1200 |

</div>

The accelerator needs an MMU, and its fast memory must sit below 1 GiB. The system disk is the
master on the A1200's own IDE port; install from the [install CD](../install/cd.md) on the IDE
slave, started from the boot floppies: the 68030 pair (`amix-1.1.2-boot-k30-1/-2.adf`) for a 68030 card,
the 68040/68060 pair (`amix-1.1.2-boot-k46-1/-2.adf`) for a 68040.
Or write an [IDE image](../install/ide-disk.md) to a CF or SD card for the master. The network
install needs a network card 1.1 drives; on
an A1200 that means an A2065 on a Zorro busboard (networking works in emulation; the
network-install route itself is untested). From 1.1.1 an X-Surf card is driven too, untested on an
A1200. No PCMCIA network cards yet.

### Memory

**Both lines:** the kernel runs only in fast memory below 1 GiB (`0x40000000`). An accelerator
that places all its memory at `0x40000000` or above cannot boot 1.1: the boot loader stops with
`no fast memory below 0x40000000 to run the kernel in`. To check, run `ShowConfig` in an AmigaOS
Shell: its memory lines give each block's address range, and one block of fast memory must start
below `$40000000`.

**68060 line:** one block of fast memory below 1 GiB (`0x40000000`), up to 128 MB. Memory outside
the block the system loads into is not used, so Zorro III memory, which AmigaOS places from
1 GiB up, is never used for the system. With a larger block the boot loader says so, for example
`amix-boot: k46 kernel: using 128 MiB of the 256 MiB here`; with no fast memory below 1 GiB it
stops with `no fast memory below 0x40000000`.

### The system disk {#system-disk}

The system disk must be on a controller the system drives:

- built into both kernels: the A3000's own SCSI, the A2091 and the A2090;
- modules on the 1.1 media: `a4091` (the A4091 and A4092), `a4kt710` (the A4000T's own SCSI),
  `gayle` (the IDE port on the motherboard of an A1200 or A4000) and `z3660scsi` (the Z3660's
  disks);
- from [1.1.1](../release-notes/1.1.1.md), the module `buddha`: the Individual Computers Buddha's
  two IDE ports, the disk on either port as master or slave, also a single drive jumpered as slave
  (tested in emulation only). The machine boots from the disk through the card's own ROM, and the
  kernel then drives it. Catweasel Z-II, its three ports: tested in emulation on both lines, the
  system disk on its first or third port, a data disk on the third and an ATAPI CD-ROM, with
  interrupt-driven I/O; not yet on a real card.

Not supported yet: other makers' SCSI cards, such as GVP's; the SCSI options of Blizzard and
Cyberstorm accelerators; the IDE ports of accelerator cards; the A1200's PCMCIA slot; on 1.1, the
Buddha. A disk on such a card can start the boot, as the boot loader reads it through the card's
own ROM, but the system then stops with `cannot mount root: errno 6`
([boot messages](../docs/known-issues.md#boot-messages)).

### Moving the system disk to another controller {#moving-disk}

From 1.1.1. The boot generation names the controller the system disk is on, so a disk moved to
another controller, say from the motherboard's IDE port to a Buddha, needs one rebuild that names
the new one. Do it before the move, or after it from a boot that mounted the root, as root:

1. `kbootset cards` gives the new controller's key `K` (and its base, when two boards of one kind
   are fitted);
2. `kbootset build --bootdev K --rootdev K --root "sd id=<id> base=<base or 00000000> unit=U
   slice=1"`, with `U` the disk's unit and `<id>` the controller's id (a Buddha is `id=12120000`,
   a Catweasel Z-II `id=12122a00`);
3. `kbootset commit`; the next boot tries it, and `mark-good`, run at the end of every boot, makes
   it the default.

There is no `--swap`: swap is always the second slice of the system disk the kernel boots from. A
generation already built with `--swap` is fine as it is.

Edit `bootdev` and `rootdev` in `/etc/default/bootset` to `K` as well, for a later repair. On a
Buddha or a Catweasel Z-II the units are fixed: port 0's master is 6 and its slave 5, port 1's
master 3 and its slave 2, and on the Catweasel's third port, port 2, the master is 1 and the
slave 0.

### Drivers

<div class="tbl" markdown>

| Hardware | Driver | Status |
|---|---|---|
| Z3660: disks (images on its SD card) | `z3660scsi` | <span class="tier t-hw">Supported · hardware</span> on the 68060 line; in the Z3660's 68030 mode <span class="tier t-emu">Supported · emulation</span> (the 1.0 built-in driver also ran on hardware) |
| Z3660: Ethernet, `zen0` | `z3660eth` | <span class="tier t-hw">Supported · hardware</span> on the 68060 line, with DHCP (an A4000T) or a fixed address; 68030 mode as the disks. No emulator has this card |
| Z3660: graphics (RTG) | `z3660rtg` | <span class="tier t-hw">Supported · hardware</span> on both lines, from [1.1.2](../release-notes/1.1.2.md). In the Z3660's 68030 mode, with `z3660rtg` 1.1.2-3: on an A4000T the graphics are found with no setting, and X came up at 1024x768 and ended cleanly. On the 68060 line, with the final 1.1.2 packages from one plain `apkg upgrade`: on an A4000D the graphics attach by AutoConfig, and `xstart` brought the default session up on them at 1024x768. Modes 640x480, 800x600, 1024x768, 1280x720, 1280x800, 1280x1024 and 1920x1080, 16-bit colour only. Needs the Z3660's RTG AutoConfig off (its default) and the `monsw` module: [X and RTG](../docs/x11.md) |
| MNT ZZ9000: graphics (RTG) | `z3660rtg`, from [1.1.2](../release-notes/1.1.2.md) | <span class="tier t-emu">Supported · emulation</span>, both lines, in Zorro II or Zorro III, alone or beside a Z3660 as its second card (`/dev/zz9001`); not yet on a real card. A Zorro III card on the 68030 line needs 1.1.2's 68030 kernel |
| MNT VA2000: graphics (RTG) | `va2000`, from [1.1.2](../release-notes/1.1.2.md) | Not yet on a real card: the VA2000 cannot be emulated, so only the install and a boot with no card fitted are tested, on both lines. The packages install its card file `/etc/display.d/va2000`, so `xstart` starts X on it (`Xrtg -card va2000`); beside another card, `card` in `/etc/display` chooses. The console stays on the Amiga's own display. Needs the card's firmware 5 or later |
| A4091 SCSI | `a4091` | <span class="tier t-emu">Supported · emulation</span>, both lines; the system disk can sit behind it. With a boot ROM that carries a CD filesystem it boots the [install CD](../install/cd.md) by itself (tested in emulation) |
| A4092 SCSI | `a4091` | <span class="tier t-hw">Supported · hardware</span> on the 68060 line, as the system disk or beside the Z3660; <span class="tier t-emu">Supported · emulation</span> on the 68030 line. Its ROM does not boot the [install CD](../install/cd.md): start from the boot floppies or the Z3660 boot disk, then install from a CD drive on it (tested on an A4000) |
| A4000T onboard SCSI (53C710) | `a4kt710` | <span class="tier t-hw">Supported · hardware</span> on the 68060 line, as the system disk; not with the Z3660 in 68030 mode (the driver does not load there). Installing onto it, from the [install CD](../install/cd.md): on the 68060 line, <span class="tier t-emu">Supported · emulation</span> |
| A3000 onboard SCSI | in both kernels | <span class="tier t-emu">Supported · emulation</span> on the 68030 line; untested on the 68060 line |
| A2091, A2090 SCSI | in both kernels | untested on 1.1 |
| Buddha IDE | `buddha`, from 1.1.1 | <span class="tier t-emu">Supported · emulation</span>, both lines: the system disk on either port, master or slave, and CD-ROM drives. Catweasel Z-II, its three ports: tested in emulation on both lines, the system disk on its first or third port, a data disk on the third and an ATAPI CD-ROM, with interrupt-driven I/O; not yet on a real card: [the system disk](#system-disk) |
| X-Surf-100 (Zorro II or Zorro III) and X-Surf Ethernet, `xsf0` | `xsurf`, from 1.1.1 | <span class="tier t-emu">Supported · emulation</span>, both lines, tested by us with DHCP or a fixed address. Users report an X-Surf-100 working on real hardware with 1.0.0-3 in two A4000D machines, each with a CyberStorm 68060: one with DHCP and traffic both ways, the other in Zorro III with the system disk on a Buddha, with DHCP, ping, telnet and ftp, after a first report of it failing that was a bad solder joint on the card, not the driver. From [1.1.2](../release-notes/1.1.2.md) (1.0.0-4, run in emulation only) it reads the X-Surf-100's link, and `xsf` prints the board, the link and the counters: [networking](../docs/networking.md) |
| A2065 Ethernet, `aen0` | in the kernels | <span class="tier t-emu">Supported · emulation</span>, both lines, with a fixed address; DHCP ran in emulation with an earlier kernel, not yet with 1.1's |
| A4000 Gayle IDE | `gayle` | <span class="tier t-hw">Supported · hardware</span> on the 68060 line (the system disk on the IDE port, or beside the Z3660 or an A4092; an ATAPI CD-ROM as slave); <span class="tier t-emu">Supported · emulation</span> on the 68030 line. A CF card works as the master only. A4000T untested; A600 planned; the A1200's own IDE port: [above](#the-a1200). Installing onto it: the master only; tested in emulation (A1200 and A4000), not yet on real hardware. |
| CD-ROM (ISO 9660 with Rock Ridge) | `cdfs` | <span class="tier t-hw">Supported · hardware</span> on the 68060 line (an ATAPI drive on the IDE port); <span class="tier t-emu">Supported · emulation</span> on the 68030 line. Read-only, for reading discs: never the system disk. Joliet, UDF and HFS untested. Installed on every 1.1 system; it loads at the first CD mount, so a machine without a CD drive spends no memory on it. Mount by card and unit, e.g. `mount -F cdfs 1,5 /cdrom` |
| Paula sound | `paula` | <span class="tier t-emu">Supported · emulation</span>: [Sound](../docs/sound.md) |

</div>

Each network card's interface name, and how to set it up: [Networking](../docs/networking.md#interfaces).

On the Z3660 up to eight disk images are SCSI units 0 to 7; a disk image's block size must be a
power of two from 512 to 4096 bytes, and a CD image is read-only.

Drivers are packages for each line (`z3660scsi-k46`, `z3660scsi-k30`, …); the images carry
the ones their machines need, and `apkg` installs the others ([boot recovery](../docs/modules.md)).

### Other hardware

Anything not listed here is untested. Tell us about it with a
[hardware support request](%SUPPORT_HARDWARE%): the machine, the accelerator and its firmware,
the controller, and what happened.
