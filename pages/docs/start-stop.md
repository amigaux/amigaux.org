---
title: "Starting and stopping safely"
---

## Starting and stopping safely

Amiga UNIX keeps data in memory and writes it to disk later. Switching off a running system can
leave the file systems to be repaired at the next boot. Always halt it first.

### Switching off

As root, logged in **on the console** (a change of run level asked for over `telnet` can stall):

```
init 0
```

It stops the services, then halts. Wait for `The system is halted; you may reboot or turn off
power.`, then 10 seconds more, and switch off. `shutdown -i0 -g0 -y` does the same (tested in
emulation on 1.1).

**If it does not halt** and the system stays up:

```
sync; sync; /sbin/uadmin 2 0
```

This halts at once, without stopping the services first. Over `telnet` your session simply ends:
that is the halt succeeding. Wait 10 seconds, then switch off.

### Restarting

On a real 68060 (the Z3660): **never** `reboot` or `shutdown -i6`. The Z3660 cannot reset the CPU
cleanly; it may not start again until you switch off and on. Halt as above, then switch off and on.

On a 68030, halting and switching off and on is the tested way as well (`shutdown -i0 -g0 -y` halts
cleanly, tested in emulation). A software reboot is not tested on 1.1; if you reboot, do it from a
root shell on the console, never over `telnet`: there it can stall until you switch off.

### After a crash or a power cut

Switch off and on. The next boot checks the file systems and repairs them; that is expected. When
a halt was clean, the check finds nothing to repair.

A new kernel on trial is not used up by that repair restart: see [boot recovery](modules.md).

<p class="next" markdown="span">[Boot recovery](modules.md) · [Known issues](known-issues.md)</p>
