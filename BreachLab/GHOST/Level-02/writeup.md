# BreachLab - Ghost Track: Level 2 → 3 (In The Shadows)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 2 → 3 (In The Shadows)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost2`
- **Goal:** Retrieve the password / credentials for `ghost3`
- **Next Connection:** `ssh ghost3@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

Analyst **Kael** compartmentalized active investigation leads into hidden files and directories across the filesystem. The objective is to leverage detailed directory listing commands (`ls -la`) and inspection tools to uncover hidden artifacts and extract the authentication password for `ghost3`.

---

## 2. Reconnaissance & Investigation Directory

Logging in via SSH as `ghost2` and inspecting the home directory:

```bash
ghost2@breachlab:~$ ls -la
total 72
drwx------ 1 ghost2 ghost2 4096 Jun  4 19:46 .
drwxr-xr-x 1 root   root   4096 May 19 12:05 ..
-rw-r--r-- 1 ghost2 ghost2  220 Jan  6  2022 .bash_logout
-rw-r--r-- 1 ghost2 ghost2 3771 Jan  6  2022 .bashrc
drwx------ 2 ghost2 ghost2 4096 May 31 22:21 .cache
drwxrwxr-x 3 ghost2 ghost2 4096 May 24 13:18 .local
-rw-r----- 1 ghost2 ghost2  153 May 19 12:05 .memo
-rw-r--r-- 1 ghost2 ghost2  807 Jan  6  2022 .profile
drwx------ 2 ghost2 ghost2 4096 May 19 19:40 .ssh
drwxrwxr-x 3 ghost2 ghost2 4096 Jun  1 20:46 .terminfo
drwxr-x--- 1 ghost2 ghost2 4096 Jun  2 21:27 investigation
```

### Entering `investigation/`

```bash
ghost2@breachlab:~$ cd investigation/
ghost2@breachlab:~/investigation$ ls -la
total 40
drwxr-x--- 1 ghost2 ghost2 4096 Jun  2 21:27 .
drwx------ 1 ghost2 ghost2 4096 Jun  4 19:46 ..
drwxr-x--- 1 ghost2 ghost2 4096 Jun  2 21:27 .leads
-rw-r----- 1 ghost2 ghost2  201 May 19 12:05 report.txt
-rw-r----- 1 ghost2 ghost2  205 May 19 12:05 summary.txt
```

### Inspecting Reports

```bash
ghost2@breachlab:~/investigation$ cat report.txt
INCIDENT REPORT — Q1 2026
Status: Classified
Prepared by: KAEL

Summary: Unauthorized access detected on segment C.
Response: Ongoing. Active leads compartmentalized.

Full details filed separately.

ghost2@breachlab:~/investigation$ cat summary.txt
OPERATIONAL SUMMARY
===================
Operation: GHOST WATCH
Status: Active

All active source files have been compartmentalized
and moved to a separate location.

This document contains no credentials.
```

---

## 3. Uncovering Hidden Leads & Flag Extraction

The directory listing revealed a hidden directory named `.leads/`.

```bash
ghost2@breachlab:~/investigation$ cd .leads/
ghost2@breachlab:~/investigation/.leads$ ls -la
total 40
drwxr-x--- 1 ghost2 ghost2 4096 Jun  2 21:27 .
drwxr-x--- 1 ghost2 ghost2 4096 Jun  2 21:27 ..
-rw-r----- 1 ghost2 ghost2   13 May 19 12:05 .source_alpha
-rw-r----- 1 ghost2 ghost2   13 May 19 12:05 .source_beta
-rw-r----- 1 ghost2 ghost2   15 May 19 12:05 .source_omega
```

### Inspecting Hidden Sources

```bash
ghost2@breachlab:~/investigation/.leads$ cat .source_alpha
7a4e91c63d2f

ghost2@breachlab:~/investigation/.leads$ cat .source_beta
bb50d8e4a11c

ghost2@breachlab:~/investigation/.leads$ cat .source_omega
H1dd3nInSh4dow
```

The valid password for `ghost3` was found inside the hidden file `.source_omega`.

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost3` |
| **Password / Flag** | `H1dd3nInSh4dow` |
| **Target SSH Command** | `ssh ghost3@204.168.229.209 -p 2222` |

---

## 5. Key Commands Reference

- `ls -la`: Lists all directory items including hidden files and folders prefixed with a dot (`.`).
- `find . -name ".*"`: Recursive search for hidden files across directories.
- `cat .<filename>`: Reading hidden dotfile content.

---

## 6. Lessons Learned

1. **Hidden Files in Linux:** Any file or directory beginning with a dot (`.`) is hidden from standard `ls` and requires the `-a` flag.
2. **Nested Hidden Directories:** Always perform recursive searches or check every subfolder with `ls -la` to ensure no nested dotfiles or hidden subdirectories are missed.
