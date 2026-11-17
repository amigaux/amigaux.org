---
title: "Services, SSH and the clock"
---

## Services, SSH and the clock

### Switching a service on or off

`/etc/rc.conf` says which services of the added packages run at boot, and holds their settings.
One line each, no blanks around `=`:

```
syslogd=yes
display=no
ifup_dhcpwait=30
```

`service=yes` or `no` switches a service; `service_key=value` is one of its settings, named in the
service's own manual page. A service with no line gets its own default, which its page states. Installing, updating or
removing a package never changes the file. A bad value is reported in the boot log,
`/var/adm/rc.log`. See `rc.conf(4)`.

The original Amiga UNIX services in `/etc/rc2.d` do not read this file.

<div class="tbl" markdown>

| Line | Default | What |
|---|---|---|
| `syslogd=` | `yes` | the system log |
| `display=` | `yes` | a graphical login at boot; nothing in 1.1 uses it yet, `display=no` switches it off for good |
| `ifup_dhcpwait=` | `20` | seconds the boot waits for a DHCP lease |
| `ifup_bound=` | `120` | seconds the whole network bring-up may take at boot |
| `dropbear=` | `yes` | the SSH server: [remote login](#remote-login) |
| `dropbear_flags=` | none | options for the SSH server, e.g. `-g`: [remote login](#remote-login) |
| `dropbear_keytime=` | `900` | seconds the first start may spend making the host key |
| `ntp=` | `yes` | setting the clock from the network: [the clock](#the-clock) |
| `ntp_servers=` | `0.pool.ntp.org 1.pool.ntp.org 2.pool.ntp.org` | time servers asked after the ones DHCP gives |

</div>

The network itself, the device nodes and swap are not switched here. Other packages say in their
own pages whether they read this file.

### Making a change take effect

At the next boot, or at once, as root:

```
/etc/init.d/syslogd stop
/etc/init.d/syslogd start
```

The script has the service's name: `/etc/init.d/syslogd`, `/etc/init.d/display`. The start reads
`/etc/rc.conf` again, so a service you set to `no` stays off. For the network, use
`ifdown` and `ifup`: [Networking](networking.md).

### Remote login

**SSH** is on in every 1.1 install: the Dropbear server, with the client `ssh` (also called
`dbclient`), `scp` and `dropbearkey`. Log in with `ssh root@<address>` or as any user.
`dropbear=no` in `/etc/rc.conf` switches the server off. See `dropbear(8)`.

- The first start makes the machine's own host key, in the background, so the boot is not held
  up; at the first boot the server answers a few minutes after power-on, later boots sooner. No
  key is shipped on any image: each machine makes its own.
- Root may log in by password or by key; an empty password is refused. To limit that, set
  `dropbear_flags=` in `/etc/rc.conf`: `-w` refuses root altogether, `-g` lets root in by key
  only, `-s` lets every user in by key only.
- There is no SFTP: from a recent OpenSSH, copy with `scp -O`.
- Logging in takes under 3 seconds on a 68060, and the key exchange under 2 seconds, the
  post-quantum hybrid included (measured on an A4000 with a Z3660); copying with `scp` runs at
  about 170 KB/s.

**`telnet` and `ftp`** are the original Amiga UNIX services, unchanged: `inetd` runs them, from
`/etc/inet/inetd.conf`. They send passwords in the clear.

Whether root may log in over `telnet` is one line in `/etc/default/login`. The first-boot
question `Do you want to allow root to log in over the network?` sets it:

- `#CONSOLE=/dev/console` (commented out): root may log in anywhere, by `telnet` too;
- `CONSOLE=/dev/console`: root only on the console.

To change it later, edit that line as root. An update of the system keeps your edit and puts any
new default beside it as `/etc/default/login.new`. The line does not apply to SSH: use
`dropbear_flags=` (above).

### The clock

With `ntp=yes`, the default, the system sets its clock from the network at boot and every hour,
and writes the time to the battery clock. It asks the time servers your DHCP server names first,
then those in `ntp_servers=`. See `ntpsync(1M)`.

- The boot does not wait for it: the first setting runs in the background.
- The hourly run is a line in root's `crontab`; `ntp=no` takes it out at the next boot.
- The pool names need a name server. Without one, `/var/adm/rc.log` says so at each boot: add a
  `dns` line to `/etc/inet/interfaces` ([changing the network](first-boot.md#network)), or give
  addresses, e.g. `ntp_servers="192.0.2.5"`.

<p class="next" markdown="span">[Networking](networking.md) · [First boot](first-boot.md)</p>
