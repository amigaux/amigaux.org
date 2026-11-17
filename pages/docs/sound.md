---
title: "Sound"
---

## Sound

Amiga UNIX plays sound through the Amiga's own sound chip, Paula, in two ways.

### `/dev/audio`: a sample stream

The Amiga UNIX audio device: a program writes samples and the system plays them. One program at a
time; a second one is refused while the first has it open.

In an emulator, switch the emulator's sound output on (in Amiberry, `sound_output=interrupts` or
better). With sound off, opening `/dev/audio` fails instead of playing.

### `/dev/paula`: Paula's four channels

The Paula driver gives one program direct use of Paula's four channels, the way a tracker plays
music on AmigaOS: the samples play from chip memory without the CPU mixing them, so music costs
little CPU time.

As root, on a 68040 or 68060:

```
apkg install paula-k46
```

and on a 68030, `paula-k30`. It is a driver, so `apkg` makes a new boot generation: switch off and
on to boot it ([boot recovery](modules.md)). It needs the 1.1 kernel; `apkg` refuses it on an
older one.

- It brings `/dev/paula`, open to every user, and the programming interface
  `/usr/include/paula.h`.
- The driver loads by itself when a program first opens `/dev/paula`; it is not loaded in safe
  mode.
- While a program has `/dev/paula` open, `/dev/audio` is refused, and the other way round.
- The tempo follows the machine's PAL or NTSC timing; the pitch follows what the program sets
  (tracker period tables assume PAL).

No program in 1.1 uses `/dev/paula` yet: it is there for programs written or ported to it. The
whole interface is in `/usr/include/paula.h`.

<span class="tier t-emu">Supported · emulation</span> Tested in emulation on both lines; not yet on
real hardware.

<p class="next" markdown="span">[Packages](../packages/index.md) · [Boot recovery](modules.md)</p>
