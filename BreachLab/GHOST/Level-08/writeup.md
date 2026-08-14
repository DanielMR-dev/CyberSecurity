# BreachLab - Ghost Track: Level 8 → 9 (Something's Running)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 8 → 9 (Something's Running)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost8`
- **Goal:** Retrieve the password / credentials for `ghost9`
- **Next Connection:** `ssh ghost9@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

Analyst **Kael** purged on-disk notes and command histories, attempting to cover operational tracks ("He cleaned the files. Wiped the logs."). However, background daemons spawned during system initialization retain active process memory and runtime environments within the virtual `/proc` filesystem. The objective is to inspect running processes owned by `ghost8` and extract sensitive environment variables from `/proc/<PID>/environ` to retrieve the password for `ghost9`.

---

## 2. Reconnaissance & Process Enumeration

Logging into the `ghost8` session and listing full process trees using `ps -ef`:

```bash
ghost8@breachlab:~$ ps -ef
UID          PID    PPID  C STIME TTY          TIME CMD
root           1       0  0 May31 ?        00:01:53 sshd: /usr/sbin/sshd -D [listener] 1 of 20-100 startups
...
root          25      18  0 May31 ?        00:00:00 runuser -u ghost8 -p -- python3 /usr/local/bin/level8-daemon.py
root          26      19  0 May31 ?        00:00:00 runuser -u ghost8 -- python3 /usr/local/bin/level8-daemon.py
...
ghost8        39      26  0 May31 ?        00:00:00 python3 /usr/local/bin/level8-daemon.py
ghost8        40      25  0 May31 ?        00:00:00 python3 /usr/local/bin/level8-daemon.py
```

### Key Observations

Two Python daemon processes (`PID 39` and `PID 40`) are actively executing under the `ghost8` user account, spawned by `runuser`.

---

## 3. Memory & Process Inspection via `/proc`

In Linux, the pseudo-filesystem `/proc` exposes kernel process data structures. A user can read process attributes (including command-line arguments and environment blocks) for all processes they own.

### Inspecting PID 39

```bash
ghost8@breachlab:~$ cat /proc/39/cmdline | tr '\0' ' '
python3 /usr/local/bin/level8-daemon.py

ghost8@breachlab:~$ cat /proc/39/environ | tr '\0' '\n'
HOSTNAME=breachlab
PWD=/
HOME=/home/ghost8
SHLVL=1
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
DEBIAN_FRONTEND=noninteractive
_=/usr/sbin/runuser
USER=ghost8
LOGNAME=ghost8
```

### Inspecting PID 40

```bash
ghost8@breachlab:~$ cat /proc/40/cmdline | tr '\0' ' '
python3 /usr/local/bin/level8-daemon.py

ghost8@breachlab:~$ cat /proc/40/environ | tr '\0' '\n'
HOSTNAME=breachlab
PWD=/
HOME=/root
SHLVL=1
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
DEBIAN_FRONTEND=noninteractive
_=/usr/bin/env
ANALYST_KEY=Pr0c_T3lls_4ll
```

The process environment block of **PID 40** reveals the sensitive variable `ANALYST_KEY`.

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost9` |
| **Password / Flag** | `Pr0c_T3lls_4ll` |
| **Source Process** | `PID 40` (`/proc/40/environ`) |
| **Target SSH Command** | `ssh ghost9@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `ps -ef` / `ps aux`: List all running system processes with associated owners and PIDs.
- `/proc/<PID>/environ`: File containing all initial environment variables of a process separated by null bytes (`\0`).
- `tr '\0' '\n'`: Translate null-byte delimiters into readable newlines for shell viewing.
- `/proc/<PID>/cmdline`: File containing the exact command line and arguments passed when launching the process.

---

## 6. Lessons Learned

1. **Process Environment Exposure:** Passing secrets via environment variables to daemon processes (especially via wrapper scripts like `runuser -p`) exposes those values in `/proc/<PID>/environ` to any user with matching UID permissions.
2. **Linux Process Forensics:** Even if bash history (`.bash_history`) and logs are cleared, active memory artifacts in `/proc` maintain full forensic fidelity until process termination.
