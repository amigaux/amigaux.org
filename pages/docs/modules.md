---
title: "Drivers, modules and boot recovery"
---

## Drivers, modules and boot recovery

The kernel and the drivers are packages, updated like any other with `apkg`. The system keeps the
kernels it can boot in its boot store (the `UNIX_Boot` partition), as *generations*: a kernel with
its modules. It keeps the generation it was installed with, the two newest good ones, and at most
one on trial.

### Updating the kernel or a driver

As root:

```
apkg update
apkg upgrade
```

When an upgrade touches the kernel or a driver, `apkg` composes a new generation and commits it
as a *trial*: `generation N committed; power-cycle to boot it`. **Switch off and on**; do not
reboot. The next boot tries the trial once.

- If it comes all the way up to multi-user, the trial becomes the new good generation.
- If it panics or hangs, switch off and on: the boot loader says
  `generation N did not reach multi-user; booting M` and starts the previous good one.

Any restart before the system is fully up spends the trial's one attempt.

A module that does not match the kernel is refused, and nothing changes. Each new kernel takes about
3 MB of the root file system. Upgrading the kernel this way is tested in emulation on the 68030 and
68040/68060 lines, not yet on real hardware.

With `bootset=manual` in `/etc/default/bootset`, `apkg` only prints the two commands,
`kbootset build` and `kbootset commit`, for you to run. `bootset=auto` is the default.

### A new boot loader

An upgrade can bring a new boot loader (the `loader-amix` package) without putting it to use.
`apkg` then ends with `the loader in /stand/loader is not on the boot store yet: kbootset
loader-install /stand/loader/boot2`, and `kbootset status` shows the same note. The system keeps
working on the old loader. You need the new one only when the release notes say so, or when
`kbootset commit` refuses with `the installed loader is version N, the kernel needs M`.

To install it, as root, then **switch off and on**:

```
kbootset loader-install /stand/loader/boot2
```

Afterwards the `booted:` line of `kbootset status` says `by the primary loader` when the new one
ran. The old loader stays on the boot store, to start if the new one does not complete a boot.

Upgrading the loader package and installing the new loader are tested in emulation on the 68030
and 68040/68060 lines, not yet on real hardware. Falling back to the old loader after such an
install is not yet tested from start to finish.

### What is running

As root, `kbootset status` shows every generation and its state, the one that booted, and each
module as loaded or not. It changes nothing. See `kbootset(1M)`.

Modules load by themselves: the boot ones at boot, a device's when the device is first opened.
To look, as root: `modadmin -s` lists the loaded modules, `modadmin -Q name` shows one.

### Going back by hand

As root on the running system, then switch off and on:

- `kbootset rollback`: the previous good generation becomes the default again. To return to the
  kernel you went back from, `kbootset build`, then `kbootset commit`, then switch off and on; that
  makes one more generation of it.
- `kbootset next previous`: boot the previous good generation once; the boot after returns to the
  default.
- `kbootset mark-bad N`: never choose generation N again.

### At boot: the loader's menu

The boot loader prints one line and waits about two seconds.

- **`p`** boots the previous good generation at once.
- **Any other key**, on the keyboard or the serial console, opens the menu. So does the left mouse
  button held when that line appears. Do not hold it from power-on: then it can make an A4091 or
  A4092 boot ROM skip its disks. Kickstart's own menu is both mouse buttons held from power-on.

The menu lists the kept generations. A digit picks one; **`s`** switches safe mode on or off
(only the drivers for the root disk and its file system load); <kbd>RETURN</kbd> boots. With the
mouse, a click moves to the next entry and a two-second hold boots it.

### When nothing boots

If a generation cannot be loaded, the loader tries the default, then the other good ones, newest
first, then the one the system was installed with, and then opens its menu. From there, boot the
installed generation, or any one in safe mode, and repair from the running system with
`kbootset rollback` or `mark-bad`.

<p class="next" markdown="span">[Packages](../packages/index.md) · [Known issues](known-issues.md)</p>
