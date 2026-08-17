# BreachLab - Phantom Track: Level 10 (The Harvest)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 10 (The Harvest)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom10`
- **Goal:** Harvest infrastructure credentials and secrets stored in unhardened application configuration files (`.env`, `config.ini`) across `/opt/`, and extract the level flag
- **Next User / Flag Code:** `bl_phtm10_ea452c951c2048b2`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
MISSION: The Harvest
===================

You are root on this box. But root on one machine is nothing.
The real value is what this machine knows about OTHER systems.

Find every credential on this box: passwords, tokens, keys, secrets.
One of them is the flag for the next level.

Check: history files, config files, environment variables,
SSH keys, application configs, process memory.
```

The objective is to conduct systematic post-exploitation credential harvesting across application configurations, directories, and environment files in `/opt/`, uncover exposed database credentials, and retrieve the next level access token (`DB_PASS`).

---

## 2. Reconnaissance & Initial Post-Exploitation Enumeration

Logging in as `phantom10` and performing baseline situational awareness:

```bash
phantom10@phantom:~$ sudo -l
Sorry, user phantom10 may not run sudo on phantom.

phantom10@phantom:~$ printenv
# No injected API keys, tokens, or plaintext secrets present in process environment

phantom10@phantom:~$ cat ~/.bash_history
cat: /home/phantom10/.bash_history: No such file or directory
```

With no direct privilege delegation in sudoers and no active command history, we pivot the audit to application deployment directories in `/opt/`.

---

## 3. Directory Auditing & Permission Analysis (`/opt/`)

Auditing subdirectories in `/opt/`:

```bash
phantom10@phantom:~$ ls -la /opt/
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
drwxr-xr-x 1 root root     4096 May 28 16:07 webapp
```

### Inspecting `/opt/webapp/` Permissions

```bash
phantom10@phantom:~$ ls -la /opt/webapp/
total 24
drwxr-xr-x 1 root root      4096 May 28 16:07 .
drwxr-xr-x 1 root root      4096 May 28 16:41 ..
-rw-r----- 1 root phantom10  146 May 28 16:07 .env
-rw-r----- 1 root phantom10   85 May 28 16:07 config.ini
drwxr-x--- 3 root phantom11 4096 May 28 16:07 repo
```

### Forensic Diagnosis of the DAC Misconfiguration

- **Files:** `/opt/webapp/.env` and `/opt/webapp/config.ini`
- **Ownership:** `root:phantom10`
- **Permissions:** `-rw-r-----` (`640`)
- **Vulnerability:** Both production configuration files grant read access to group `phantom10`, allowing our session user to inspect sensitive database connection strings and secrets directly.

---

## 4. Credential Harvesting & Secrets Extraction

### 4.1. Reading `/opt/webapp/config.ini`

```ini
phantom10@phantom:~$ cat /opt/webapp/config.ini
[database]
host = db.internal
port = 5432
user = admin
password = Pr0d_DB_P4ss_2026!
```

- **Harvested Secret:** Administrative credentials for PostgreSQL database (`admin:Pr0d_DB_P4ss_2026!`).

### 4.2. Reading `/opt/webapp/.env`

```bash
phantom10@phantom:~$ cat /opt/webapp/.env
DB_HOST=db.internal
DB_USER=webapp
DB_PASS=bl_phtm10_ea452c951c2048b2
REDIS_URL=redis://localhost:6379
SECRET_KEY=a1b2c3d4e5f6
```

- **Harvested Secret (Flag):** The production database password (`DB_PASS`) contains the level access token: `bl_phtm10_ea452c951c2048b2`.

---

## 5. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 10) |
| **Current User** | `phantom10` |
| **Vulnerability Type** | Hardcoded Plaintext Secrets in Application Configs |
| **Vulnerable Files** | `/opt/webapp/.env`, `/opt/webapp/config.ini` |
| **Admin Database Password** | `Pr0d_DB_P4ss_2026!` (`admin@db.internal:5432`) |
| **App Database Password / Flag** | `bl_phtm10_ea452c951c2048b2` |
| **Discovered Flag** | `bl_phtm10_ea452c951c2048b2` |
| **Artifact Path** | `/opt/webapp/.env` |

---

## 6. Key Commands & Concepts Reference

- `ls -la /opt/webapp/`: Audit application directory structure and discretionary file permissions.
- `cat /opt/webapp/.env`: Inspect environment files for hardcoded API keys, JWT secrets, and database credentials.
- `cat /opt/webapp/config.ini`: Extract static infrastructure configuration parameters.
- `grep -r "AKIA" / 2>/dev/null`: Search files for AWS access key patterns during credential hunting.

---

## 7. Lessons Learned & Defensive Takeaways

1. **Never Store Hardcoded Secrets in Config Files:** Storing plaintext credentials in `.env`, `.ini`, or settings files on disk creates severe exposure risks if any local user or web service is compromised. Secret management solutions (*HashiCorp Vault*, *AWS Secrets Manager*, *Key Vault*) should be utilized to inject ephemeral credentials dynamically in memory.
2. **Strict Web Service Group Isolation:** Application files should be owned exclusively by the dedicated runtime service account (e.g., `www-data` or a dedicated system daemon) with permissions restricted to `600` or `640` where only the service group has read access. Interactive users must never belong to service groups.
3. **Application Forensics in Lateral Movement:** In offensive operations and Red Teaming, auditing `/opt/`, `/var/www/`, configuration repos, and local git histories often yields high-privilege credentials to external systems, databases, and cloud infrastructures without needing kernel-level exploits.
