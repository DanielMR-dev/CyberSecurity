# BreachLab - Ghost Track: Level 1 → 2 (Name Game)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 1 → 2 (Name Game)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost1`
- **Goal:** Retrieve the password / credentials for `ghost2`
- **Next Connection:** `ssh ghost2@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

Analyst **Kael** intentionally created files with unusual names (spaces, leading dashes, multiple dots) to confuse standard shell commands and careless analysts. The objective is to properly quote and escape filenames to read the artifacts and recover the credentials for `ghost2`.

---

## 2. Reconnaissance & Directory Listing

Connecting via SSH as `ghost1` and listing directory contents with details:

```bash
ghost1@breachlab:~$ ls -la
total 96
-rw-r----- 1 ghost1 ghost1   13 May 19 12:05  -
-rw-r----- 1 ghost1 ghost1   13 May 19 12:05  --help
drwx------ 1 ghost1 ghost1 4096 Jun  4 19:46  .
drwxr-xr-x 1 root   root   4096 May 19 12:05  ..
-rw-r----- 1 ghost1 ghost1   13 May 19 12:05  ...
-rw-r--r-- 1 ghost1 ghost1  220 Jan  6  2022  .bash_logout
-rw-r--r-- 1 ghost1 ghost1 3771 Jan  6  2022  .bashrc
drwx------ 2 ghost1 ghost1 4096 May 31 22:32  .cache
drwxrwxr-x 3 ghost1 ghost1 4096 May 24 13:08  .local
-rw-r--r-- 1 ghost1 ghost1  807 Jan  6  2022  .profile
drwx------ 2 ghost1 ghost1 4096 May 19 14:59  .ssh
drwxrwxr-x 3 ghost1 ghost1 4096 Jun  1 20:44  .terminfo
-rw-r----- 1 ghost1 ghost1  228 Apr 17 09:44  MANIFEST
-rw-r----- 1 ghost1 ghost1   15 May 19 12:05 'file name'
```

### Inspecting `MANIFEST`

```bash
ghost1@breachlab:~$ cat MANIFEST
NOTES — KAEL
────────────
I named my files to watch careless analysts
give up before they even read them.

Most people who poke around this directory
will quit before they open the first one.

— KAEL
```

---

## 3. Handling Special Filenames & Password Extraction

The directory contains files with special characters:
- Files starting with dashes (`-`, `--help`): Treated as flags/options unless specified as `./-` or `./--help`.
- Files with spaces (`file name`): Require escaping (`file\ name`) or quoting (`'file name'`).
- Files with multiple dots (`...`): Require explicit referencing (`./...` or `cat ...`).

### Reading `'file name'`

```bash
ghost1@breachlab:~$ cat file\ name
D4shIsN0tAFl4g
```

Alternatively using single or double quotes:
```bash
ghost1@breachlab:~$ cat 'file name'
D4shIsN0tAFl4g
```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost2` |
| **Password / Flag** | `D4shIsN0tAFl4g` |
| **Target SSH Command** | `ssh ghost2@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Shell Escaping Reference

- **Files with spaces:** `cat 'file name'` or `cat "file name"` or `cat file\ name`
- **Files starting with dashes:** `cat ./-` or `cat ./--help` or `cat -- -` (using `--` to signal the end of command-line options)
- **Files with dots:** `cat ./...`

---

## 6. Lessons Learned

1. **Shell Escaping & Quoting:** Spaces and special characters in filenames require single quotes, double quotes, or backslash escapes.
2. **Disambiguating Options from Filenames:** Prepending `./` or using the `--` delimiter prevents commands from interpreting leading hyphens as CLI flags.
