# Building the **remote.exe** Project

## Overview

The **remote.exe** project is built on a fork of **libvncserver**. The provided source bundle contains only files modified from a specific upstream commit. It does **not** include the full library.

You must:

1. Clone the upstream repository
2. Check out the forked commit
3. Replace files with the provided modified versions
4. Build dependencies and the project

---

## 1 — Get libvncserver

```bash
git clone https://github.com/LibVNC/libvncserver.git
cd libvncserver
git checkout 1c5d989ab50ee2baeb2fda717bc9c622516ccf98
```

Copy the provided files into this directory, overwriting originals.

---

## 2 — Build Dependencies

```bash
./buildDeps.sh -a <arch>
```

**Options**

* `-a` Target architecture: `x64` (default) or `ARM64`

**Examples**

```bash
./buildDeps.sh
./buildDeps.sh -a ARM64
```

---

## 3 — Build Project

```bash
./build.sh -a <arch> [-c]
```

**Options**

* `-a` Target architecture: `x64` (default) or `ARM64`
* `-c` Clean build directory first

**Examples**

```bash
./build.sh
./build.sh -a ARM64 -c
```
