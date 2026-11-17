---
title: "Known issues"
---

## Known issues

### Starting and stopping

- **No software reboot on a real 68060.** `reboot` and `shutdown -i6` can leave the 68060 unable to
  start until you switch off and on. Halt, then switch off and on:
  [starting and stopping safely](start-stop.md).
- **Halt from the console.** A change of run level asked for over `telnet` can stall. Use `init 0`
  from a root shell on the console; if it does not halt, `sync; sync; /sbin/uadmin 2 0`.
- **Wait before switching off.** The Z3660 keeps your disks as files on its SD card and may still be
  writing for a few seconds after the halt: wait 10 seconds.
- **`shutdown` can return before the system halts.** After a lot of disk writing on a machine with
  16 MB, `shutdown` may print its messages and return to the prompt while the system keeps running;
  it halts by itself within five minutes. Do not switch off until the console says the system is
  halted. If `who -r` still shows the old run level half a minute after the shutdown, type
  `/sbin/init 0` (or `/sbin/init 6` for a restart) once more; the system then halts at once.

### What the boot messages mean {#boot-messages}

- **`no fast memory below 0x40000000 to run the kernel in`**, from the boot loader: the machine
  has no fast memory below 1 GiB, and the kernel runs only there. An accelerator that places all
  its memory at `0x40000000` or above cannot boot 1.1: [memory](../hardware/index.md#memory).
- **`cannot mount root: errno 6`**, from the kernel: it cannot open the system disk (errno 6: no
  such device). Most often the disk is on a controller this version has no driver for, such as a
  Buddha on 1.1: the boot loader read the disk through the card's own ROM, but the kernel cannot.
  Move the disk to a [supported controller](../hardware/index.md#system-disk); for the IDE images,
  the IDE port on the motherboard.

### The Z3660

- **It can stop after loading the Kickstart**, rarely. Switch off and on.
- **Every card has the same Ethernet address** until you change `mac_address` in `z3660cfg.txt`
  (digits only): [the Z3660 page](../install/z3660-sd.md).

### Disks and file systems

- **A file system holds at most 2047 MiB**; on a bigger disk, make more partitions.
- **On the motherboard's IDE port a single drive must be jumpered as master** (or sit beside a
  master): a drive alone as slave is not found. A CD-ROM alone on the port works, without
  interrupts. The Buddha and Catweasel ports do not have this limit.
- **A second disk on the A3000's own SCSI** has stopped Kickstart 3.2 from booting the first one.
- **`/etc/rdb -V` shows a slice of 2 GiB or more with a negative size in bytes.** The block counts
  on the same line are right; only the display is wrong.
- **A file over 256 MiB needs the `ulimit` raised.** Every login has it raised already, to 2 GiB,
  in `/etc/default/login`.
- **On a 68030 without a floating-point unit** making a `ufs` file system fails with
  `Bad System Call`.

### Memory and swap

- **A program's data and address space have no limit by default**, soft or hard, not the
  original 16 MiB; only the stack is limited, to 16 MiB. To set a limit, use `ulimit -d` (data)
  and `ulimit -v` (address space), with a size in KiB, in the shell or in a profile
  (`/etc/profile` for everyone); it holds for that shell and what it starts. A later kernel brings
  the original 16 MiB back as the default soft limits, with the hard limits unlimited so that they
  can be raised.
- **The memory programs can use is the swap size**, whatever the RAM. The installer offers a swap
  partition by memory: 64 MB on a machine with less than 32 MB, 128 MB with 32 MB or more, never
  more than a quarter of the disk. Every boot adds the whole partition, or as much as the kernel
  takes, and says so on the console when it is less. For more swap, make a file `/SWAPFILE`, for
  example `dd if=/dev/zero of=/SWAPFILE bs=1024k count=64`: every boot adds it. `swap -a` adds
  swap only until the next reboot; `swap -l` shows what is in use.

### Installing

- **A disk at SCSI id 5 is not offered as a target**: the installer looks for the CD there.
- **A reinstall can keep the old layout's size.** The installer offers a disk's own size, but in
  two cases it keeps the size of the layout already on the disk, and says so: on the A3000's own
  SCSI controller, and for a disk on a third or fourth disk card (the IDE port beside a Z3660 and
  a Zorro SCSI card, for example).
- **Another bootable disk can win over the new install.** The new disk's boot partition has
  priority 2; Kickstart boots the bootable partition with the highest priority on any disk. An
  AmigaOS disk at the usual 0 loses to it; an older Amix install, a disk behind an A4091 or A4092
  or on the Z3660, or a boot disk can win. The installer names any disk whose priority is above
  the new one's. Lower that partition's priority or raise the new disk's (HDToolBox, or the Early
  Startup menu for one boot), or take that disk out, and take out any boot floppy or boot disk
  before the first boot.

### Networking

- **`netstat -rn` does not work**; `netstat -in` does. The default route is in
  `/var/adm/rclog/ifup`: [networking](networking.md).
- **The package repository is reached by name**, `pkg.amigaux.org`. A fixed address with no name
  server (**n** to `Enable DNS?` at the first boot) does not reach it, and `apkg` says it cannot
  resolve the name, until you add a `dns` line to `/etc/inet/interfaces`:
  [changing the network](first-boot.md#network).
- **If the disk fills while `apkg` downloads a package**, `apkg` reports it as a network error and
  tries three times before giving up; nothing is left installed. Check the free space with
  `df -k /` first: the download goes to `/var/apkg/cache` on the root.
- **An upload from the system can arrive short.** A program on Amix that closes a network
  connection right after sending can lose the end of what it sent, with no error. The original
  `ftp` client does this when it sends a file. `scp` and `rsync` are not affected
  ([remote login](services.md#remote-login)); after an FTP upload, compare the size at the other
  end. Downloads from the system's own FTP server arrive whole: `ftpdfix`, in the base set, fixes
  that server.

### The clock

- **`setclk -p` prints the year as three digits** from 2000 on (2026 is 126); the clock itself is
  right.

### Not yet tested on 1.1

- The 68030 line on real hardware (it is tested in emulation).
- `useradd -m` and `userdel -r`.
- Adding a second disk.

### The kernel

- **No crash dump.** A panic's message on the console screen is the only record.
- **`sysdef` stops with `/etc/master.d not a directory`**: in 1.1 the drivers are modules. Use
  `modadmin -s` for what is loaded, `kbootset status` for the kernel you booted.
- **`crash` does not work on the 68060 kernel** yet, and `adb -k` there reads the kernel's own
  variables right but can show wrong values at addresses from `0x40000000` on (the kernel heap, the
  u-area); read those through `/dev/kmem`. On the 68030 kernel both work; there `crash`'s `od`
  needs its physical form, `od -p` (for example `od -p -x ninode 1`).
- **68060: `cas2` and a misaligned `cas` stop the program.** The other integer instructions the
  68060 lacks (64-bit multiply and divide, `movep`, `cmp2`, `chk2`) are emulated. No installed
  program uses either.
- **Ending an X session** has twice crashed a 68060 machine.

### X

- **X on the Z3660's RTG needs X11R6.3**: the *x11* set from the install CD, the *full* set over
  the network, or `apkg install x11r6.3`. On a standard install `xstart` uses the Amiga's own
  display: [X and RTG](x11.md).
- **X on the Z3660 is not yet tested on 1.1**, nor is a graphical login at boot (`start xdm`):
  [X and RTG](x11.md).

### For programmers

- **Two faults of the original socket library.** A program that peeks (`recv` with `MSG_PEEK`) at
  a listening socket can no longer accept on it: every later `accept` fails with `EINVAL`; do not
  peek at listeners (`poll` and `select` on them are fine). A non-blocking `send` that meets a
  nearly full socket reports all its bytes as sent and drops what did not fit (with no room at all
  it fails with `ENOMEM`, not `EAGAIN`); on non-blocking stream sockets use `write(2)`, which
  returns the count that went and `EAGAIN`. Blocking sends are not affected, nor are Python and
  programs built on GNU Pth.
- **Closing a TCP socket right after writing can lose the data not yet sent.** Call
  `shutdown(fd, 1)`, read to end of file, then `close`. A kernel fix is planned after 1.1.

Not listed here? Report it in [%SUPPORT_REPO%](%SUPPORT_ISSUES%); see [Support](../about/index.md#support).
