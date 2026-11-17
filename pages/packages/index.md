## Packages

`apkg` fetches packages from **pkg.amigaux.org**, from the 1.1 tree. Every 1.1 install has it set up.

<div class="term"><span class="u"># apkg update</span>              fetch the catalog
<span class="u"># apkg list</span>                what is there, and what you have
<span class="u"># apkg list installed</span>      only what you have
<span class="u"># apkg search gzip</span>
<span class="u"># apkg info less</span>
<span class="u"># apkg install less</span>        with its dependencies
<span class="u"># apkg upgrade less</span>
<span class="u"># apkg upgrade</span>             everything that has a newer version
<span class="u"># apkg upgrade apkg</span>        the client itself
<span class="u"># apkg remove less</span></div>

Run `apkg update` before an install or upgrade. A download goes to `/var/apkg/cache` on the root:
check the free space with `df -k /` first, as a full disk shows only as a network error. Settings:
`/etc/apkg.conf` (`repo`, timeouts); `-v` with any command, such as `apkg -v update`, prints them
first. A 1.1 system has `repo=http://pkg.amigaux.org/1.1`.

A package file you downloaded yourself installs with `pkgadd -d <file> all`; leave out `all` and
`pkgadd` asks which package to install. Allow about twice the file's size free in `/var/tmp`.
`libcfix` replaces a file of the core package, `/usr/lib/libc.so.1`: install it with
`apkg install libcfix`. `apkg` will not remove an essential package, such as `libcfix` or
`amix-base`.

The name `pkg.amigaux.org` is looked up through the name servers your DHCP server gives, or the
ones you set; without any, add a `dns` line to `/etc/inet/interfaces`
([changing the network](../docs/first-boot.md#network)).

The full list: [the catalog](https://pkg.amigaux.org/1.1/catalog), one package per line, or
`apkg list` on the machine.

### The base set

Every 1.1 install has these packages from its first boot. The essential ones cannot be removed.

- `amix-base`: the base system: the boot steps and `/etc/rc.conf` that switches them on and off;
  the network set-up from `/etc/inet/interfaces` (DHCP or a fixed address, and name servers); swap
  added at boot; the clock set from time servers at boot and hourly; the graphical login; and
  `man`. Essential.
- `amixrt`: the runtime library (`libamixrt.so.1`) that shared libraries built with the current
  compiler need, one copy for every program that loads them. Essential.
- `cdfs`: reads CDs. The CD filesystem's mount helper (`mount -F cdfs <card>,<unit> <dir>`,
  read-only, with `/cdrom` as the mount point); the filesystem itself is a kernel module that
  loads when you mount.
- `dhcp-client`: gets the machine's network address from a DHCP server and keeps it, with the
  name servers and time servers the server names.
- `dropbear`: SSH, the server and client in one small program, with `scp`. On by default;
  `dropbear=no` in `/etc/rc.conf` turns the server off.
- `ftpdfix`: the original FTP server (`in.ftpd`) with downloads that arrive whole: it no longer
  cuts off the end of a passive-mode download while reporting `226 Transfer complete`; a client
  that never closes is let go after 60 s. Essential.
- `heirloom-tar`: the system `tar`, replacing the 1992 one, which crashed on modern archives.
  Reads GNU, ustar and pax archives, long names, and gzip or bzip2 compressed ones. Essential:
  there is no original copy to put back.
- `libcfix`: the system's C library (`libc.so.1`) with two memory-allocation faults fixed: a
  program that ran short of memory could have its data overwritten without any error (Vim saved
  files with lines missing). Essential.
- `rdate`: sets the clock from a time server (SNTP or the older time protocol). The base system's
  clock sync runs it at boot and hourly; there is nothing to configure.
- `syslog`: starts the system log at boot, from the original `/etc/syslog.conf`; `syslogd=no` in
  `/etc/rc.conf` turns it off.
