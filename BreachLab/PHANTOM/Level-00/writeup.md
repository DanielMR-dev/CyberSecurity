# BreachLab - Phantom Track: Level 0 (Recon Gateway)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 0 (Recon Gateway)
- **Current User:** `phantom0`
- **Goal:** Perform full situational awareness recon and retrieve the initial access flag
- **Next User / Flag Code:** `bl_phtm0_5f2a6f9c60ed3d72`

---

## 1. Scenario & Objectives

Upon initiating the **Phantom Track**, Level 0 serves as the initial post-exploitation gateway (*Recon Gateway*). The `BRIEFING` outlines the primary objective:
> *"You have shell access on a compromised host. Before you escalate, you need to know where you are.*
> - *What OS and kernel version is this?*
> - *Who else is on this box?*
> - *What services are running?*
> - *What defenses are active?*
> *The flag is hidden somewhere only a thorough recon finds."*

---

## 2. Comprehensive System Reconnaissance

Logging in as `phantom0` and establishing baseline situational awareness:

### OS & Kernel Fingerprinting

```bash
phantom0@phantom:~$ uname -a
Linux phantom 6.8.0-117-generic #117-Ubuntu SMP PREEMPT_DYNAMIC Tue May  5 19:26:24 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux

phantom0@phantom:~$ cat /etc/os-release
PRETTY_NAME="Ubuntu 22.04.5 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04.5 LTS (Jammy Jellyfish)"
ID=ubuntu
```

- **Operating System:** Ubuntu 22.04.5 LTS (Jammy Jellyfish)
- **Kernel:** Linux 6.8.0-117-generic x86_64

### Process Tree & Container Detection

```bash
phantom0@phantom:~$ ps -ef
UID          PID    PPID  C STIME TTY          TIME CMD
root           1       0  0 May31 ?        00:00:02 sshd: /usr/sbin/sshd -D [listener] 0 of 20-100 startups
root          42       1  0 May31 ?        00:00:06 /usr/sbin/cron -P
root          92       1  0 May31 ?        00:00:00 /bin/bash /entrypoint.sh
root         107     104  0 May31 ?        00:00:46 python3 /usr/local/bin/docker-socket-emulator.py unix:/var/run/docker.so
root         109     105  0 May31 ?        00:00:46 python3 /usr/local/bin/docker-socket-emulator.py 0.0.0.0:2375
root         110     106  0 May31 ?        00:00:00 phantom-host-init infinity
phantom8  244125  244124  0 Jun02 ?        00:00:00 python3 -c  import sys, time, ctypes # yama ptrace_scope=1
phantom0  615676  615675  0 12:13 pts/0    00:00:00 -bash
```

> [!NOTE]
> Process trees containing `/entrypoint.sh`, `phantom-host-init`, and `docker-socket-emulator.py` indicate that the user shell is operating inside an isolated containerized environment (Docker/Kubernetes).

---

## 3. Defense Audit & Hardening Restrictions

Testing standard network diagnostic binaries reveals hardening:

```bash
phantom0@phantom:~$ ss -tlpn
-bash: /usr/bin/ss: Permission denied

phantom0@phantom:~$ netstat -tlpn
-bash: /usr/bin/netstat: Permission denied
```

- **Restricted Utilities:** `ss` and `netstat` have restricted DAC permissions or file capabilities preventing low-privilege users from listing open sockets and local listeners.

---

## 4. Filesystem Auditing & Hidden Dotfile Discovery

To overcome network reconnaissance restrictions, a deep recursive search across the filesystem was performed to locate flag artifacts:

```bash
phantom0@phantom:~$ find / -name "*flag*" -type f 2>/dev/null
/opt/.phantom_l0_flag
/var/lib/phantom-flags/level2_flag
/var/lib/phantom-flags/level5_flag
/var/lib/phantom-flags/level3_flag
/var/lib/phantom-flags/level6_flag
/var/lib/phantom-flags/level7_flag
/var/lib/phantom-flags/level8_flag
/var/lib/phantom-flags/level4_flag
/usr/local/bin/phantom-hide-flags.sh
```

### Inspecting `/opt` Permissions

```bash
phantom0@phantom:~$ ls -la /opt
total 80
drwxr-xr-x 1 root root     4096 May 28 16:41 .
drwxr-xr-x 1 root root     4096 May 29 09:56 ..
-rw-r----- 1 root phantom0   26 May 28 16:07 .phantom_l0_flag
drwx------ 3 root root     4096 May 28 16:41 docker-host-sim
drwxr-xr-x 2 root root     4096 May 28 16:07 host-ns
drwxr-xr-x 3 root root     4096 May 28 16:07 leaky-vessels
drwxr-xr-x 1 root root     4096 May 28 16:07 maintenance
drwxr-xr-x 2 root root     4096 May 28 16:07 vault
...
```

### DAC & Dotfile Analysis
- **Hidden Dotfile (`.`):** The filename `.phantom_l0_flag` starts with a dot, hiding it from default `ls` listings.
- **Discretionary Access Control (DAC):** Permissions are `-rw-r-----` (`640`), owned by `root:phantom0`. Because our current session belongs to group `phantom0`, group read permissions grant full access.

### Reading the Flag

```bash
phantom0@phantom:~$ cat /opt/.phantom_l0_flag
bl_phtm0_5f2a6f9c60ed3d72
```

---

## 5. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 0) |
| **Current User** | `phantom0` |
| **Discovered Flag** | `bl_phtm0_5f2a6f9c60ed3d72` |
| **Artifact Path** | `/opt/.phantom_l0_flag` |
| **File Permissions** | `-rw-r-----` (`root:phantom0`) |

---

## 6. Key Commands Reference

- `uname -a` & `cat /etc/os-release`: System, distribution, and kernel architecture enumeration.
- `ps -ef`: Full process hierarchy audit to identify background daemons, security agents, and container runtimes.
- `find / -name "*flag*" -type f 2>/dev/null`: Systematic search for unlinked or exposed artifacts across the filesystem while suppressing permission errors.

---

## 7. Lessons Learned & Takeaways

1. **Systematic Situational Awareness:** Thorough static reconnaissance (OS version, kernel release, container emulation indicators) forms the prerequisite baseline before selecting privilege escalation paths.
2. **Hidden Files in System Paths:** Dotfiles outside of home directories (e.g. `/opt/.<file>`) are often used to conceal scripts or credentials; wildcard recursive searches reveal these instantly.
3. **Containerized Architecture Awareness:** The presence of `docker-socket-emulator.py` and container namespaces in `/opt` hints at upcoming privilege escalation vectors centered around container escapes and Docker socket exploitation.
