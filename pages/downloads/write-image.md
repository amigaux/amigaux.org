---
title: "Writing the image"
---

## Writing the image

First check and unzip the download: [Checking a download](verify.md). The image is then
3600 MiB, or 1800 MiB for an IDE or Buddha image.

### The 68060 image: copy it to the Z3660 card {#k46}

The Z3660 keeps its disks as files on its SD card. **Do not write the image to the card**: copy it
as a file into the `hdf/` folder on the card's exFAT partition, beside the other disk images. Then
point a preset at it: [Install on a Z3660](../install/z3660-sd.md).

### The 68030 image: write it to a disk {#k30}

The image is a whole disk. Write it to a SCSI disk of 3600 MiB or more, which then goes at
SCSI id 6; the rest of a larger disk stays unused. With a SCSI emulator, use the unpacked file as
the emulated disk's image, at id 6. Everything on the disk is lost.

**Linux:** find the disk with `lsblk`, then, with the disk at `/dev/sdX`:

```
sudo dd if=amix-1.1.2-k30-4g.img of=/dev/sdX bs=4M conv=fsync status=progress
```

**macOS:** find the disk with `diskutil list`, then, with the disk at `/dev/diskN`:

```
diskutil unmountDisk /dev/diskN
sudo dd if=amix-1.1.2-k30-4g.img of=/dev/rdiskN bs=4m
```

**Windows:** use a raw disk-image writer, for example Win32 Disk Imager, and pick the whole disk.

Check the device name twice: `dd` overwrites whatever disk you name. Then
[install](../install/68030-disk.md).

### The IDE images: write them to a CF or SD card {#ide}

The image is a whole disk of 1800 MiB. Write it the same way, to a CF or SD card of 2 GB or more,
which then goes on the IDE port as the master; the rest of a larger card stays unused. Everything
on the card is lost.

```
sudo dd if=amix-1.1.2-k46-ide-2g.img of=/dev/sdX bs=4M conv=fsync status=progress
```

Use `amix-1.1.2-k30-ide-2g.img` for a 68030. On macOS and Windows, as for the 68030 image above.
Then [install](../install/ide-disk.md).

The Buddha images, `amix-1.1.2-k46-buddha-2g.img` and `amix-1.1.2-k30-buddha-2g.img`, are written
the same way, to a disk or card that then goes on the Buddha's first port as the master:
[on a Buddha](../install/ide-disk.md#buddha).
