## GitHub

All source is on [GitHub](%GITHUB_ORG%). Every public repository, one line each.

Reporting a problem and not sure which repository? Use [%SUPPORT_REPO%](%SUPPORT_ISSUES%); see [Support](../about/index.md#support).

### amix: the system

<ul class="repo">
<li><a href="https://github.com/amigaux/amix">amigaux/amix</a> — everything that builds Amiga UNIX: the kernels, loadable modules, drivers, packages and install media</li>
<li><a href="https://github.com/amigaux/amix-system">amigaux/amix-system</a> — the Commodore 2.1/2.1c system files the build takes as its input</li>
<li><a href="https://github.com/amigaux/amix-distfiles">amigaux/amix-distfiles</a> — the upstream source archives the build fetches</li>
</ul>

Inside amix:

<ul class="repo">
<li><a href="https://github.com/amigaux/amix/tree/master/kernel/port">kernel/port</a> — the 68040/68060 kernel, built from our fork of the port below</li>
<li><a href="https://github.com/amigaux/amix/tree/master/kernel/k30">kernel/k30</a> — the 68030 kernel</li>
<li><a href="https://github.com/amigaux/amix/tree/master/kernel/dlm">kernel/dlm</a> — loadable modules: the boot loader, the module core, the ABI kit, <code>kbootset</code></li>
<li><a href="https://github.com/amigaux/amix/tree/master/kernel/drivers">kernel/drivers</a> — the hardware drivers, one directory each: A4091, CD filesystem, Gayle IDE, Paula, Z3660 Ethernet, graphics and SCSI</li>
<li><a href="https://github.com/amigaux/amix/tree/master/kernel/modules">kernel/modules</a> — generic modules: the monitor switch, the RAM disk, random numbers</li>
<li><a href="https://github.com/amigaux/amix/tree/master/userland/base">userland/base</a> — the base system: networking and DHCP, <code>rc.conf</code>, the display set-up, the system log</li>
<li><a href="https://github.com/amigaux/amix/tree/master/userland/pkgtools">userland/pkgtools</a> — <code>apkg</code> and the package tools</li>
<li><a href="https://github.com/amigaux/amix/tree/master/userland/packages">userland/packages</a> — the packaged software, one directory per package</li>
<li><a href="https://github.com/amigaux/amix/tree/master/media">media</a> — boot and install media</li>
</ul>

### Our forks and tools

<ul class="repo">
<li><a href="https://github.com/amigaux/amix-040-060-port">amigaux/amix-040-060-port</a> — the 68040/68060 port amix builds from (fork of <a href="https://github.com/asokero/amix-040-060-port">asokero/amix-040-060-port</a>)</li>
<li><a href="https://github.com/amigaux/amix-z3660rtg">amigaux/amix-z3660rtg</a> — graphics driver for the Z3660, a fork of isoriano1968's ZZ9000 driver</li>
<li><a href="https://github.com/amigaux/core1-z3660-amix">amigaux/core1-z3660-amix</a> — Z3660 core 1 as a coprocessor for AMIX, by isoriano1968</li>
<li><a href="https://github.com/amigaux/amix-paula">amigaux/amix-paula</a> — <code>/dev/paula</code>, the Paula audio driver, by isoriano1968</li>
<li><a href="https://github.com/amigaux/hydra-amix">amigaux/hydra-amix</a> — Hydra ethernet driver, by isoriano1968</li>
<li><a href="https://github.com/amigaux/amix-gayle-ide">amigaux/amix-gayle-ide</a> — A4000 Gayle IDE driver (fork of <a href="https://github.com/hmlio/amix-gayle-ide">hmlio/amix-gayle-ide</a>)</li>
<li><a href="https://github.com/amigaux/amix-cdfs">amigaux/amix-cdfs</a> — CD filesystem, ported from <a href="https://github.com/reinauer/ODFileSystem">reinauer/ODFileSystem</a></li>
<li><a href="https://github.com/amigaux/gcc14-cross-amix">amigaux/gcc14-cross-amix</a> — the GCC 14 cross toolchain for the packages (fork of <a href="https://github.com/asokero/gcc14-cross-amix">asokero/gcc14-cross-amix</a>)</li>
<li><a href="https://github.com/jusii/gcc-cross-amix">jusii/gcc-cross-amix</a> — the <code>m68k-cbm-sysv4</code> cross toolchain (fork of <a href="https://github.com/isoriano1968/gcc-cross-amix">isoriano1968/gcc-cross-amix</a>)</li>
<li><a href="https://github.com/jusii/Z3660-amix">jusii/Z3660-amix</a> — Z3660 firmware with Amiga UNIX support; 1.1's is the branch <a href="https://github.com/jusii/Z3660-amix/tree/amix-1.1">amix-1.1</a></li>
<li><a href="https://github.com/amigaux/grimoire">amigaux/grimoire</a> — the full technical details</li>
</ul>

### Collaborators' own repositories

<ul class="repo">
<li><a href="https://github.com/asokero/amix-040-060-port">asokero/amix-040-060-port</a> — runs Amiga UNIX on the 68040 and 68060</li>
<li><a href="https://github.com/asokero/amix-unix-boot">asokero/amix-unix-boot</a> — lets <code>unix_boot</code> load a kernel on a 68040 or 68060</li>
<li><a href="https://github.com/asokero/xrtg-amix">asokero/xrtg-amix</a> — Xrtg, an X11R5 RTG server</li>
<li><a href="https://github.com/asokero/va2000-amix">asokero/va2000-amix</a> — MNT VA2000 graphics driver</li>
<li><a href="https://github.com/asokero/quake-amix">asokero/quake-amix</a> — Quake, as a benchmark</li>
<li><a href="https://github.com/asokero/gcc14-cross-amix">asokero/gcc14-cross-amix</a> — a GCC 14 cross toolchain</li>
<li><a href="https://github.com/isoriano1968/amix-gate">isoriano1968/amix-gate</a> — kernel-side drivers and modules by isoriano1968, the ZZ9000 graphics driver among them</li>
<li><a href="https://github.com/isoriano1968/amix-userland">isoriano1968/amix-userland</a> — X11R6.3, Mesa and more, by isoriano1968</li>
<li><a href="https://github.com/isoriano1968/gcc-cross-amix">isoriano1968/gcc-cross-amix</a> — the original cross toolchain</li>
<li><a href="https://github.com/hmlio/amix-gayle-ide">hmlio/amix-gayle-ide</a> — A4000 Gayle IDE driver</li>
</ul>

### Built on

<ul class="repo">
<li><a href="https://github.com/shanshe/Z3660">shanshe/Z3660</a> — the Z3660 accelerator firmware</li>
<li><a href="https://github.com/reinauer/ODFileSystem">reinauer/ODFileSystem</a> — the CD filesystem we ported</li>
<li><a href="https://github.com/BlitterStudio/amiberry">BlitterStudio/amiberry</a> — the Amiberry emulator</li>
</ul>
