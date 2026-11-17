---
title: "Serial console"
---

## Serial console

Two serial lines matter: the Amiga's own serial port, where Amix can offer a login, and the
Z3660's console, where its firmware talks.

### The Amiga's serial port: a login

The 25-pin serial port on the Amiga, `/dev/term/ser` in Amix. Settings: 9600 baud, 8 data bits,
no parity, 1 stop bit; no hardware flow control (set your terminal to XON/XOFF or none). Connect it
to a PC with a null-modem cable, or a USB serial adapter with a null-modem adapter.

The login there is off as installed. To switch it on, as root:

```
pmadm -e -p serial -s ser
```

This takes effect at once and stays on. Press <kbd>RETURN</kbd> on the serial line and it answers
`ser login:`. `pmadm -l -p serial` shows whether it is on; `pmadm -d -p serial -s ser` switches it
off again.

The kernel's messages stay on the screen, and on a 68060 so does the first-boot dialog. On a
68030 the boot loader's own lines also appear on the serial port, up to `amix-boot: starting the
kernel`. A key pressed on the serial line during the loader's two seconds opens its menu
([boot recovery](modules.md)).

**When it does not work:**

- No prompt: the login is off; switch it on as above, then press <kbd>RETURN</kbd>.
- Garbled characters: set your terminal to 9600, 8N1.
- Nothing in either direction: use a null-modem cable, not a straight one.
- On the PC, only one program at a time can use the serial adapter: close any other that holds it.

### The Z3660's own console

The Z3660 has a USB serial port of its own for its firmware: the banner, the boot messages, its
boot menu. The card powers it: it appears on USB a few seconds after the Amiga is switched on and
goes when it is switched off, so open it then. Settings: 115200 baud, 8N1, no flow control; any
terminal program will do.

It shows nothing of Amix on a real 68060: it is not the Amiga's serial port.

**Careful with its boot menu.** The firmware's menu (press `C` during the countdown at power-on,
on the Amiga's keyboard or this console) acts on single keys, and some act at once, with no
question first. Do not press `D`, `U`, `F`, `O`, `M` or `K` unless you mean it: `D` rewrites the
card's logic, and a power cut during it can leave the card unusable. Never type words or paste
text into it.

<p class="next" markdown="span">[Boot recovery](modules.md) · [Known issues](known-issues.md)</p>
