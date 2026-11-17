---
title: "Users"
---

## Users

### At the first boot

`Would you like to create a user account? [n]`: answer **y** to make one. It asks the login name
and the full name, makes the account with the Korn shell (`/usr/bin/ksh`), creates its home
directory `/home/name` from the files in `/etc/skel`, and lets you give it a password.

`/home` is a partition of its own (1424 MiB on the 1.1 images), mounted at every boot, so your
files stay apart from the system.

### Later, as root

```
useradd -s /usr/bin/ksh -c "Full Name" -m name
passwd name
```

`-m` makes the home directory under `/home`. To remove an account with its home:
`userdel -r name`.
Neither `-m` nor `-r` is tested on 1.1 yet.

### What every login gets

- The search path has the added software ahead of the original, and packages add theirs through
  `/etc/profile.d`.
- `man` shows the pages of the added software too.
- A file can be up to 2 GiB.

<p class="next" markdown="span">[Services, SSH and the clock](services.md) · [Disks](disks.md)</p>
