---
title: "Disks"
---

## Disks

### The installed disk

The 1.1 images hold four partitions: the root, swap, the boot store and `/home`
([the layout](../downloads/index.md#layout)). In Amix the disk at SCSI id 6 is `c6d0`, and its
partitions are slices:

- `/dev/dsk/c6d0s1`: the root (`/dev/rdsk/c6d0s1` is the same slice, raw);
- `/dev/dsk/c6d0s2`: swap;
- slice 3: the boot store, used only by the boot loader and `kbootset`;
- slice 4: `/home`.

`/etc/vfstab` lists what is mounted at boot, one line each, in seven columns: the device, the raw
device to check, the mount point, the file-system type, the check pass, mount at boot, options.
For example the root:

```
/dev/dsk/c6d0s1 /dev/rdsk/c6d0s1 / ufs 1 no -
```

### Sizes

- A file system holds at most 2047 MiB. On a bigger disk, make more partitions.
- A single file can be up to 2 GiB.

### Adding a disk

There is no tested way yet to add a second disk to a 1.1 system.

- On the A3000's own SCSI, a second disk has stopped Kickstart 3.2 from booting the first one:
  do not add one there.
- On a 68030 without a floating-point unit, making a `ufs` file system fails with
  `Bad System Call`.

<p class="next" markdown="span">[Users](users.md) · [Boot recovery](modules.md)</p>
