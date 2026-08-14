# BreachLab - Ghost Track: Level 0 → 1 (First Contact)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 0 → 1 (First Contact)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost0`
- **Goal:** Retrieve the password / credentials for `ghost1`
- **Next Connection:** `ssh ghost1@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

The previous analyst (**Kael**) abandoned his terminal workstation in a hurry. The objective is to navigate the filesystem, locate residual artifacts left behind, and recover the authentication credentials for the next level (`ghost1`).

---

## 2. Initial Reconnaissance

Upon logging into the `ghost0` session, the home directory contains an initial `README` file and a `workspace` folder:

```bash
ghost0@breachlab:~$ ls
README  workspace
```

### Inspecting `README`

```bash
ghost0@breachlab:~$ cat README
ANALYST WORKSTATION — KAEL
Last active: 2026-03-28 02:47 UTC
Status: Abandoned

If you're reading this, you found my terminal.
I left in a hurry. Didn't have time to clean up.

Nothing in this shell is hidden. It's just here.
If you can't see it, you're not looking hard enough.

Don't leave traces.

— KAEL
```

### Checking Hidden Files

Checking permissions and directory contents:

```bash
ghost0@breachlab:~$ ls -la
total 72
drwx------ 1 ghost0 ghost0 4096 Jun  1 20:44 .
drwxr-xr-x 1 root   root   4096 May 19 12:05 ..
-rw-r--r-- 1 ghost0 ghost0  220 Jan  6  2022 .bash_logout
-rw-r--r-- 1 ghost0 ghost0 3771 Jan  6  2022 .bashrc
drwx------ 2 ghost0 ghost0 4096 May 31 22:21 .cache
drwxrwxr-x 3 ghost0 ghost0 4096 May 28 14:39 .local
-rw-r--r-- 1 ghost0 ghost0  807 Jan  6  2022 .profile
drwx------ 2 ghost0 ghost0 4096 May 31 15:42 .ssh
drwxrwxr-x 3 ghost0 ghost0 4096 Jun  1 16:20 .terminfo
-rw-r----- 1 ghost0 ghost0  312 Apr 17 09:44 README
drwxr-x--- 1 ghost0 ghost0 4096 May 19 12:05 workspace
```

---

## 3. Directory Navigation & Artifact Discovery

### Step 1: Navigating to `workspace/`

```bash
ghost0@breachlab:~$ cd workspace/
ghost0@breachlab:~/workspace$ ls
archive  notes.txt
```

### Step 2: Reading Operational Notes

```bash
ghost0@breachlab:~/workspace$ cat notes.txt
OPERATIONAL NOTES — KAEL
========================
Target: internal network segment 10.4.x.x
Method: passive recon, no active scanning
Status: ongoing

Credentials filed separately in archive/.
Do not store passwords in plaintext notes.
```

The notes state that credentials were saved under the `archive/` directory.

### Step 3: Accessing `archive/` and Extracting Password

```bash
ghost0@breachlab:~/workspace$ cd archive/
ghost0@breachlab:~/workspace/archive$ ls -la
total 24
drwxrwxrwx 1 ghost0 ghost0 4096 May 19 12:05 .
drwxr-x--- 1 ghost0 ghost0 4096 May 19 12:05 ..
-rw-r----- 1 ghost0 ghost0   15 May 19 12:05 credentials

ghost0@breachlab:~/workspace/archive$ cat credentials
W3lc0m3T0Gh0st
```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost1` |
| **Password / Flag** | `W3lc0m3T0Gh0st` |
| **Target SSH Command** | `ssh ghost1@204.168.229.209 -p 2222` |

---

## 5. Key Commands Reference

- `ls` / `ls -la`: List directory contents including permissions and hidden dotfiles.
- `cd <directory>`: Change current working directory.
- `cat <file>`: Concatenate and display the content of files.

---

## 6. Lessons Learned

1. **Information Breadcrumbs:** Operational notes and leftover analyst artifacts often disclose where sensitive data or credentials have been filed.
2. **Directory Structure Traversal:** Methodical exploration of subdirectories (`workspace/` → `archive/`) is crucial for baseline Linux enumeration.
