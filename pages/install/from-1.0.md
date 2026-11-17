---
title: "Coming from 1.0"
---

## Coming from 1.0

amigaux 1.1 is a **clean install**. There is no upgrade from 1.0: nothing of a 1.0 system is
carried over, and an installer that finds Amix on a disk erases it.
From 1.1 on, later releases upgrade an installed 1.1 system in place, with its packages through
`apkg`: 1.1 is the last release that only installs clean.

**Back up first.** Copy off everything you want to keep: your own files, and any settings you
changed under `/etc`. Copy them to another machine or another disk before you start.

**On a Z3660 you can keep 1.0.** The 1.1 image is a new file on the card; the 1.0 image can stay
beside it. Map only one of them as a bootable disk in the preset you boot.

**A 1.0 system you keep** gets its packages from the 1.0 tree, at the top of the server:
`repo=http://pkg.amigaux.org` in `/etc/apkg.conf`, as 1.0 has it.

Then: [Install](index.md).
