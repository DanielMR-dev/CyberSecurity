# BreachLab - Ghost Track: Level 18 → 19 (Wrong User / SUID)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 18 → 19 (Wrong User)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost18`
- **Goal:** Retrieve the password / credentials for `ghost19`
- **Next Connection:** `ssh ghost19@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

The MOTD banner for Level 18 outlines the challenge:
> *"There's a binary on this system that belongs to another user — but the permission bits on it mean something special. Read them. Use the tool."*

The objective is to search the filesystem for custom binaries possessing the SetUID (`SUID`) permission bit, analyze permissions associated with target user `ghost19`, and execute the privileged binary to read the flag for the next level.

---

## 2. Reconnaissance & SUID Binary Enumeration

Logging in via SSH as `ghost18`:

```bash
ghost18@breachlab:~$ ls -la
total 48
drwx--S--- 1 ghost18 ghost18 4096 Jun  4 18:09 .
...
```

### Searching for SUID Binaries

Using `find` to discover all files with the SUID bit (`-perm -4000` or `-u=s`):

```bash
ghost18@breachlab:~$ find / -perm -4000 -type f 2>/dev/null
/usr/local/bin/ghost-reader
/usr/local/bin/ghost-archivist
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/openssh/ssh-keysign
/usr/bin/mount
/usr/bin/umount
/usr/bin/newgrp
/usr/bin/su
```

### Inspecting Custom SUID Binaries

Checking file ownership and permissions for the discovered binaries under `/usr/local/bin/`:

```bash
ghost18@breachlab:~$ ls -la /usr/local/bin/ghost-reader
-rwsr-x--- 1 ghost19 ghost18 819664 May 19 12:04 /usr/local/bin/ghost-reader

ghost18@breachlab:~$ ls -la /usr/local/bin/ghost-archivist
-rwsr-x--- 1 root ghost22 819664 May 19 12:04 /usr/local/bin/ghost-archivist
```

#### Permission Analysis: `/usr/local/bin/ghost-reader`
- **Owner:** `ghost19`
- **Group:** `ghost18` (allowing members of `ghost18` read and execute access)
- **Permissions:** `-rwsr-x---` (Mode `4750`)
- **SUID Bit (`s`):** When executed by a user in the `ghost18` group, the process runs with the **Effective User ID (EUID)** of `ghost19`.

---

## 3. Privilege Abuse & Flag Extraction

Executing `/usr/local/bin/ghost-reader` reads the protected target credential under the identity of `ghost19`:

```bash
ghost18@breachlab:~$ /usr/local/bin/ghost-reader /home/ghost19/flag
SU1D_Fl1p

# Running without arguments also prints the target flag:
ghost18@breachlab:~$ /usr/local/bin/ghost-reader
SU1D_Fl1p
```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost19` |
| **Password / Flag** | `SU1D_Fl1p` |
| **SUID Binary** | `/usr/local/bin/ghost-reader` |
| **Binary Owner / Group** | `ghost19` : `ghost18` |
| **Target SSH Command** | `ssh ghost19@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `find / -perm -4000 -type f 2>/dev/null`: Find all files across the filesystem with the SUID (`4000`) bit enabled.
- `find / -perm /6000 -type f 2>/dev/null`: Search for files with either SUID (`4000`) or SGID (`2000`) bits set.
- `ls -la <binary>`: Inspect permission strings (`-rwsr-xr-x`) to identify whether SUID (`s`/`S`) or SGID is configured.

---

## 6. Lessons Learned

1. **SUID (Set User ID) Mechanics:** SUID allows unprivileged users to run executables with the security context and privileges of the file owner (EUID).
2. **Access Control Granularity:** Setting specific group permissions (`ghost18`) alongside SUID (`ghost19`) creates a controlled privilege escalation bridge intended specifically for authorized group members.
