---
title: "Networking"
---

## Networking

The network comes up at every boot from `/etc/inet/interfaces`. The first boot writes it from
your answers; after that you edit it as root. See `interfaces(4)`.

### The interfaces {#interfaces}

Each network card is an interface, named by its driver and a number from 0. Use that name in
`/etc/inet/interfaces` and with `ifup`, `ifdown` and `ifconfig`.

<div class="tbl" markdown>

| Name | What it is | Driver | Bus | Tested |
|---|---|---|---|---|
| `zen0` | the Z3660's own Ethernet | `z3660eth-k46` or `-k30`, in every system installed from the 1.1.1 or 1.1.2 files | on the Z3660 | on real hardware, on the 68060 line, with DHCP and with a fixed address |
| `aen0` | an A2065 | in both kernels | Zorro II | in emulation only, on both lines, with a fixed address |
| `xsf0` | an X-Surf-100 or an X-Surf; a second board is `xsf1` (not yet tested) | `xsurf-k46` or `-k30`, from [1.1.1](../release-notes/1.1.1.md), in every system installed from the 1.1.1 or 1.1.2 files | X-Surf-100: Zorro II or Zorro III; X-Surf: Zorro II | in emulation only, on both lines, with DHCP and with a fixed address |
| `lo0` | the loopback, `127.0.0.1` | in both kernels | | always up; it needs no line |

</div>

An A2065 can share a machine with one X-Surf, not with two. The cards: [supported
hardware](../hardware/index.md#drivers).

### DHCP

```
* dhcp
```

Every network card asks a DHCP server for its address. This is the default. Add a line
`hostname dhcp` if the machine should also take its name from the server; otherwise a DHCP server
never changes it.

### A fixed address

One line per card: its name, `static`, the address with its prefix length, and the router.

```
zen0 static 192.0.2.20/24 gw 192.0.2.1 name amix
dns 192.0.2.1
domain example.org
```

Put your card's name first: `zen0` here, or `aen0` or `xsf0` ([the interfaces](#interfaces)). A
card's station (MAC) address can stand in for its name, so one disk image can serve several
machines. A card is set up by the line with its station address, else the line with its name,
else the `*` line; with none of them it stays down. A mistake in its line also leaves it down.

`domain` only completes this machine's full name in `/etc/inet/hosts`; it is never added to the
names you look up.

### Applying a change

Check the file first: `ifup -n` prints every mistake with its line number. Then, as root on the
console (over telnet, `ifdown` cuts your own session), take the card down and up again by its
name, for example:

```
ifdown zen0; ifup zen0
```

A new `name` takes effect at once; programs already running keep the old name until they start
again.

### An X-Surf {#x-surf}

- **A system installed from the 1.1.1 or 1.1.2 files:** the driver is already there. The first boot
  offers the card as `xsf0`, with DHCP or a fixed address.
- **A card fitted later to such a system:** with the `* dhcp` line it comes up by DHCP at the
  next boot. Otherwise add a line for `xsf0`, DHCP or a fixed address as above; check it with
  `ifup -n`, then on the console `ifdown xsf0; ifup xsf0`.
- **A system installed from the 1.1 files:** it needs the driver, from the repository, over a
  network card it already has. As root, `apkg update; apkg upgrade`, then
  `apkg install xsurf-k46` (`xsurf-k30` on a 68030), and restart; then set up `xsf0` as above
  ([adding them to an installed 1.1](../release-notes/1.1.1.md#upgrade)). With no other way onto
  the network, install again from the 1.1.1 files.

### What it is now

- `ifconfig zen0`, with the card's name (`lo0` for the loopback): its address and flags. Name
  each card; do not rely on `ifconfig -a`.
- `netstat -in`: the interfaces and their counters. (`netstat -rn` does not work on this system.)
- `dhcpc -q zen0`, with the card's name: the lease a DHCP card holds, with its router and name
  servers.
- The default route that was set: `/var/adm/rclog/ifup`, the log of the last boot's bring-up.

### When it does not come up

- `/var/adm/rclog/ifup` and the boot log `/var/adm/rc.log`: what the bring-up did.
- `/var/adm/dhcpc.log`: what DHCP did.
- A slow DHCP server: the boot waits 20 seconds for a lease. `ifup_dhcpwait=30` in
  `/etc/rc.conf` waits longer.
- Two Z3660s on one network need different station addresses:
  [the Z3660 page](../install/z3660-sd.md).

<p class="next" markdown="span">[Services, SSH and the clock](services.md) · [First boot](first-boot.md)</p>
