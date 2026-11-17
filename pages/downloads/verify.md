---
title: "Checking a download"
---

## Checking a download

`SHA256SUMS` lists one line per file: its SHA-256 and its name. It covers both the zip files you
download and the `.img` files inside them, so you can check each before and after unzipping. Put
it in the folder that holds your downloads, then check them there.

**Linux:**

```
sha256sum -c --ignore-missing SHA256SUMS
```

Every file you have prints `OK`. Anything else, download that file again.

**macOS:**

```
shasum -a 256 amix-1.1.2-k46-4g.zip
```

Compare the long number it prints with the file's line below or in `SHA256SUMS`.

**Windows (PowerShell):**

```
Get-FileHash -Algorithm SHA256 .\amix-1.1.2-k46-4g.zip
```

Compare the `Hash` it prints with the file's line below or in `SHA256SUMS` (upper or lower case
does not matter).

Use the name of the file you downloaded.

### Unzipping {#unzip}

Each zip holds one `.img` file of 3600 MiB, or 1800 MiB for an IDE or Buddha image; make sure there is room
for it.

- **Linux and macOS:** `unzip amix-1.1.2-k46-4g.zip`
- **Windows:** right-click the zip, *Extract All*; or in PowerShell,
  `Expand-Archive .\amix-1.1.2-k46-4g.zip -DestinationPath .`

Then check the `.img` the same way, with its own line, and [write the image](write-image.md).

### The 1.1.2 sums {#sums}

```
eb8fb17f642589367e535d12b902bfdd6326c072a2174891390d9a34fa6cfa60  amix-1.1.2-k46-4g.zip
045e57d829d86ddaab9ce3c8702d07f88138dcf2f522515b636c1c4335ba857e  amix-1.1.2-k46-4g.img
468cbaf28a71a03c63436ac77468cda3de6f4c5bd89ddca301fd7e1963fd62e9  amix-1.1.2-k30-4g.zip
39f1ba16eaf4702c5d8c51bc3f4ce5e4065b5c67b33cdaefceec0cdee9400188  amix-1.1.2-k30-4g.img
c4ba761ed6f03bfdb68fa2bf4246cd5450f421dd8b3ea15879f876a756882408  amix-1.1.2-k46-ide-2g.zip
8a88d9fc42175cf1f96c389359ad68352640eecff55c74ff18c98728f9a30aaf  amix-1.1.2-k46-ide-2g.img
a8c285d64723a61fa8fdb6c5974c6bcdc4d9a3a6ca8f0d18af077d9cf0a3f2a5  amix-1.1.2-k30-ide-2g.zip
393fd83a165f8e6cdeed51a91b3efd8ccc61fabd713fdaa0fdc3c38986e965f2  amix-1.1.2-k30-ide-2g.img
ee7557a1ae2fce24a4a4dfe0a48b9775b6132d74d9c0f9f88507094be651df1f  amix-1.1.2-k46-buddha-2g.zip
e23e3013d8d11cfe21026047bf467b9bcc681cfef50ace61c000126f26ab960d  amix-1.1.2-k46-buddha-2g.img
c1e256d5eeb186bed9c192a7a4937b0984e2f49fe64615da906ae6468ba945c5  amix-1.1.2-k30-buddha-2g.zip
118da6cd2c2289472a9fd9bae45df08bf87532ac50489709c57b6b9aa739114f  amix-1.1.2-k30-buddha-2g.img
3b7c2d9b073ed80748499c2d79fbb84c3c175ab828435389fdde269d72fed18e  amix-1.1.2-install.iso
1df02131544289562673bd64d08ef58f3b978bdbbbdac759ecdf51d4158c2f77  amix-1.1.2-netinstall.iso
975d1a854c71acdf73db6ec06620799c84e4bc6520e3ce284c298f7e0cfd5f9c  amix-1.1.2-boot-k46-1.adf
ab022f5843143bd2638424a814e6b74eb532d2df2a60ee22ca1fe525527caa0d  amix-1.1.2-boot-k46-2.adf
da62c84fd468dbb36b2435356a844edaea6591f247b75b5125419a142e1d085f  amix-1.1.2-boot-k30-1.adf
5f1ebe7752a76bdae378574f61edba805b605193c7e3db3a2a2d1281981786af  amix-1.1.2-boot-k30-2.adf
2c7e8fc0f80506636d9ef2182c2fd8020448c5854352fb1256277970be5edfd1  amix-1.1.2-boot-z3660.hdf
d3a44c8b71a83b7650c81cfe7727ec1324a088937a9dbf37a82f06841589993a  amix-1.1.2-z3660-sd-kit.zip
6b4bc2feaa7020898c5669e60f9c7e0385356257090e36189c4f6128cb0570f8  z3660-firmware-1.1-CDEB9618.bin
910b685455a55516d5031d6b22d872b5689796fc603da10b734c6c6b8fc7994a  z3660-firmware-1.1-README.txt
```

The earlier files' sums are in each release's own `SHA256SUMS`:
[1.1.1](%MEDIA_1_1_1%/SHA256SUMS), [1.1](%MEDIA_1_1%/SHA256SUMS).
