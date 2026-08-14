# BreachLab - Ghost Track: Level 11 → 12 (Wrapped Three Deep)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 11 → 12 (Wrapped Three Deep)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost11`
- **Goal:** Retrieve the password / credentials for `ghost12`
- **Next Connection:** `ssh ghost12@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

Analyst **Kael** nested his operational payload three layers deep using different compression and archiving formats ("Identify first, unpack second. Keep going."). The objective is to iteratively identify archive formats with `file` and decompress each layer using the corresponding Linux utility (`tar`, `bzip2`, `gzip`) to uncover the plaintext credentials for `ghost12`.

---

## 2. Reconnaissance & Artifact Inspection

Logging in via SSH as `ghost11` and listing directory contents:

```bash
ghost11@breachlab:~$ ls -la
total 64
drwx------ 1 ghost11 ghost11  4096 Jun  4 20:47 .
drwxr-xr-x 1 root    root     4096 May 19 12:05 ..
...
-rw-r----- 1 ghost11 ghost11 10240 May 19 12:05 data.wrapped
```

---

## 3. Step-by-Step Multi-Layer Extraction

### Layer 1: POSIX Tar Archive

Inspecting `data.wrapped` format:

```bash
ghost11@breachlab:~$ file data.wrapped
data.wrapped: POSIX tar archive (GNU)
```

Extracting the tar archive:

```bash
ghost11@breachlab:~$ tar -xf data.wrapped
ghost11@breachlab:~$ ls
core.txt.gz.bz2  data.wrapped
```

---

### Layer 2: Bzip2 Compressed Data

Inspecting `core.txt.gz.bz2`:

```bash
ghost11@breachlab:~$ file core.txt.gz.bz2
core.txt.gz.bz2: bzip2 compressed data, block size = 900k
```

Decompressing with `bzip2 -d`:

```bash
ghost11@breachlab:~$ bzip2 -d core.txt.gz.bz2
ghost11@breachlab:~$ ls
core.txt.gz  data.wrapped
```

---

### Layer 3: Gzip Compressed Data

Inspecting `core.txt.gz`:

```bash
ghost11@breachlab:~$ file core.txt.gz
core.txt.gz: gzip compressed data, was "core.txt", last modified: ...
```

Decompressing with `gzip -d`:

```bash
ghost11@breachlab:~$ gzip -d core.txt.gz
ghost11@breachlab:~$ ls
core.txt  data.wrapped
```

---

### Reading Plaintext Payload

```bash
ghost11@breachlab:~$ cat core.txt
Unwr4pp3d_Thr33
```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost12` |
| **Password / Flag** | `Unwr4pp3d_Thr33` |
| **Nested Structure** | `tar` → `bzip2` → `gzip` → `core.txt` |
| **Target SSH Command** | `ssh ghost12@204.168.229.209 -p 2222` |

---

## 5. Compression Format Triage Reference

| Format Identified (`file`) | Required Extension | Extraction Command |
| :--- | :--- | :--- |
| **POSIX tar archive** | `.tar` / any | `tar -xf <file>` |
| **bzip2 compressed data** | `.bz2` | `bzip2 -d <file.bz2>` or `bunzip2 <file>` |
| **gzip compressed data** | `.gz` | `gzip -d <file.gz>` or `gunzip <file>` |
| **Zip archive data** | `.zip` | `unzip <file.zip>` |
| **XZ compressed data** | `.xz` | `unxz <file.xz>` or `xz -d <file.xz>` |
| **7-zip archive data** | `.7z` | `7z x <file.7z>` |

---

## 6. Lessons Learned

1. **Format Identification Over Extension:** Filesystem extensions can be omitted or intentionally misleading; always query file headers using the `file` utility before attempting extraction.
2. **Decompression Tool Requirements:** Tools like `gzip` and `bzip2` enforce standard file extensions (`.gz`, `.bz2`) during decompression unless reading from standard input (`zcat`, `bzcat`, or `gzip -dc`).
