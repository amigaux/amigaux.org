---
title: "First boot and network"
---

## First boot and network

A new system asks these once, on the console, under the heading `Amiga UNIX system
configuration`. Wait for each question to appear before you type: keys pressed while the system
is still starting are lost.

<div class="tbl kv" markdown>

| Prompt | Answer |
|---|---|
| `What is the nodename of this machine? (RETURN: the name DHCP gives, else amix-xxxx)` | <kbd>RETURN</kbd>, or a name |
| `What is this machine's network domain? []` | <kbd>RETURN</kbd>, or your domain |
| (time zone menu) | <kbd>RETURN</kbd> keeps the default, or the number of your zone |
| `Do you want to configure networking? [y]` | <kbd>RETURN</kbd> |
| `Use DHCP to configure the network? [y]` | <kbd>RETURN</kbd> if your network has a DHCP server; **n** for a fixed address (below) |
| `What is the package repository host? [pkg.amigaux.org]` | <kbd>RETURN</kbd> |
| `Would you like to assign a password to all of the system accounts? [y]` | <kbd>RETURN</kbd>, then the password twice: this is root's |
| `Would you like to assign a password to the guest account? [y]` | **n** unless you want a guest login |
| `Do you want to allow root to log in over the network? [y]` | <kbd>RETURN</kbd> to allow telnet as root |
| `Would you like to create a user account? [n]` | <kbd>RETURN</kbd>, or **y** to make one now |
| `Are you using an A2024 or Moniterm high resolution monitor? [n]` | <kbd>RETURN</kbd> |
| `Do you wish to configure X Windows for a color graphics card? [n]` | <kbd>RETURN</kbd>: this is for the A2410; X on the Z3660 is below |
| `Do you wish to configure Netnews for either local or networked operation? [n]` | <kbd>RETURN</kbd>; asked only when news is installed |
| `Do you want the system logging daemon enabled? [y]` | <kbd>RETURN</kbd> |
| `Do you wish to change any of these? [n]` | <kbd>RETURN</kbd> after checking the summary |

</div>

Without a network card (an A2065 or the Z3660's), the network questions are skipped. A card fitted
later asks a DHCP server for its address at its first boot.

DHCP also sets the name servers (`/etc/resolv.conf`). If your DHCP server gives none, `apkg` cannot
reach `pkg.amigaux.org` until the system has one: add a `dns` line to `/etc/inet/interfaces`
([changing the network](#network)).

### A fixed address instead of DHCP {#static}

Answer **n** to `Use DHCP to configure the network?`, then:

<div class="tbl kv" markdown>

| Prompt | Answer |
|---|---|
| `Which interface do you want to use? [1]` | asked only with two network cards: the number of the one to use |
| `What is this machine's network address? []` | e.g. `192.0.2.20` |
| `What is the netmask? [255.255.255.0]` | <kbd>RETURN</kbd> |
| `What is the default gateway? [none]` | your router, e.g. `192.0.2.1` |
| `Enable DNS? [n]` | **y** asks for one or two name servers. With **n**, `apkg` cannot reach `pkg.amigaux.org` until the system has one: add a `dns` line to `/etc/inet/interfaces` later ([changing the network](#network)) |
| `What is the package repository host? [pkg.amigaux.org]` | <kbd>RETURN</kbd> |

</div>

### The clock

The date and time are not asked: the system clock comes from the battery clock. Set it from
AmigaOS, and never into the future. With time sync on, the network keeps it right:
[the clock](services.md#the-clock).

### Logging in

The first boot reaches the login prompt in a few minutes, including the first-boot questions.
Then `login: root` with the password you just set.

- Services are switched on and off in `/etc/rc.conf`, e.g. `syslogd=no`: see `rc.conf(4)`.
- `man` shows the pages of the added software as well as the original ones; `man -a` shows both
  where a name has two.
- A file can be up to 2 GiB.
- The network comes up from `/etc/inet/interfaces`; the log of the last boot's bring-up is
  `/var/adm/rclog/ifup`.

### X {#x}

Answer **n** to the dialog's X question: it is for the A2410 colour card. To start X after the
first boot: [X and RTG](x11.md).

### Changing the network later {#network}

Edit `/etc/inet/interfaces` as root. One line per network card, for example:

```
zen0 static 192.0.2.20/24 gw 192.0.2.1
dns 192.0.2.1
```

or `* dhcp` for DHCP on every card. Check the file with `ifup -n`: it prints every mistake with its
line number. Then apply it on the console (over telnet, `ifdown` cuts your own session):

```
ifdown zen0; ifup zen0
```

Use your card's name in place of `zen0`: [the interfaces](networking.md#interfaces). A new `name`
takes effect at once; programs already running keep the old name until the next start. See
`interfaces(4)`.

<p class="next" markdown="span">[Packages](../packages/index.md) · [Known issues](known-issues.md)</p>
