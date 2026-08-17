# BreachLab - Phantom Track: Level 11 (Token Hunter)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 11 (Token Hunter)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom11`
- **Goal:** Conduct Git repository forensics, bypass Git dubious ownership restrictions (CVE-2022-24765), recover historical credentials in commit diffs (`git log -p`), and extract the level flag
- **Next User / Flag Code:** `bl_phtm11_dcad1d818b255fe7`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
MISSION: Token Hunter
====================

Credentials are not just passwords. Modern systems use tokens.
JWT, API keys, cloud credentials, service account tokens.

This machine connects to cloud services and internal APIs.
Find every token. Decode what you can. One token is the flag.
```

The objective is to search for tokens and credentials across deployment paths, identify deceptive honeypot tokens in Kubernetes service account paths, audit the web application repository in `/opt/webapp/repo/`, configure Git safe directory exceptions, examine commit history diffs for redacted secrets, and extract `/opt/webapp/repo/.env` historical secrets.

---

## 2. Reconnaissance & Honeypot Identification

Logging in as `phantom11` and checking standard cloud/token paths:

```bash
phantom11@phantom:~$ ls -la /var/run/secrets/kubernetes.io/serviceaccount/ 2>/dev/null
total 12
drwxr-xr-x 2 root root 4096 May 28 16:07 .
drwxr-xr-x 3 root root 4096 May 28 16:07 ..
-rw-r--r-- 1 root root  176 May 28 16:07 token

phantom11@phantom:~$ cat /var/run/secrets/kubernetes.io/serviceaccount/token
eyJhbGciOiJSUzI1NiIsImtpZCI6IkN1OHRBS0g3T0k2dHlhYjd3In0.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6ZGVmYXVsdCJ9.FAKE_TOKEN
```

- **Honeypot Analysis:** The K8s service account token is a decoy (`FAKE_TOKEN`), indicating active defensive mechanisms designed to divert automated scanners.

---

## 3. Auditing the Git Repository (`/opt/webapp/repo/`)

Inspecting permissions and contents of `/opt/webapp/repo/`:

```bash
phantom11@phantom:~$ ls -la /opt/webapp/repo/
total 16
drwxr-x--- 3 root phantom11 4096 May 28 16:07 .
drwxr-xr-x 1 root root      4096 May 28 16:07 ..
-rw-r----- 1 root phantom11   36 May 28 16:07 .env
drwxr-x--- 8 root phantom11 4096 May 28 16:07 .git

phantom11@phantom:~$ cat /opt/webapp/repo/.env
APP_SECRET=REDACTED
DB_URL=REDACTED
```

The current working directory `.env` file has been sanitized to `REDACTED`. However, the `.git` version control metadata directory is intact and group-readable by `phantom11`.

---

## 4. Overcoming Git Dubious Ownership (CVE-2022-24765)

Attempting to run Git commands directly inside `/opt/webapp/repo` triggers a security restriction:

```bash
phantom11@phantom:/opt/webapp/repo$ git log -p
fatal: detected dubious ownership in repository at '/opt/webapp/repo'
To add an exception for this directory, call:

        git config --global --add safe.directory /opt/webapp/repo
```

### Security Mechanism & Bypass

- **Dubious Ownership Protection:** Git enforces that repository owners must match the current user's UID to prevent unauthorized execution of repository-level hooks or config aliases.
- **Bypass Configuration:** Adding an exception in our user's global `~/.gitconfig` grants permission to inspect the root-owned repository:

```bash
phantom11@phantom:/opt/webapp/repo$ git config --global --add safe.directory /opt/webapp/repo
```

---

## 5. Git Archaeology & Secret Recovery (`git log -p`)

We inspect the complete commit patch history to recover previous revisions of `.env`:

```bash
phantom11@phantom:/opt/webapp/repo$ git log -p
commit f18e67d9f66e1330dcbb6576009a94f41311d662 (HEAD -> master)
Author: dev <dev@internal>
Date:   Thu May 28 16:07:31 2026 +0000

    remove secrets

diff --git a/.env b/.env
index 1db2a85..c935363 100644
--- a/.env
+++ b/.env
@@ -1,2 +1,2 @@
-APP_SECRET=bl_phtm11_dcad1d818b255fe7
-DB_URL=postgres://admin:secret@db:5432/prod
+APP_SECRET=REDACTED
+DB_URL=REDACTED

commit 51f5b2aa88df8bbd35902998597ae13cf33f720d
Author: dev <dev@internal>
Date:   Thu May 28 16:07:31 2026 +0000

    initial config

diff --git a/.env b/.env
new file mode 100644
index 0000000..1db2a85
--- /dev/null
+++ b/.env
@@ -0,0 +1,2 @@
+APP_SECRET=bl_phtm11_dcad1d818b255fe7
+DB_URL=postgres://admin:secret@db:5432/prod
```

- **Extracted Flag (`APP_SECRET`):** `bl_phtm11_dcad1d818b255fe7`
- **Database URL:** `postgres://admin:secret@db:5432/prod`

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 11) |
| **Current User** | `phantom11` |
| **Vulnerability Type** | Secret Leak in Git Commit History |
| **Bypassed Control** | Git Dubious Ownership (`safe.directory`) |
| **Repository Path** | `/opt/webapp/repo/.git` |
| **Discovered Flag** | `bl_phtm11_dcad1d818b255fe7` |
| **Recovered Database URL** | `postgres://admin:secret@db:5432/prod` |

---

## 7. Key Commands & Concepts Reference

- `git config --global --add safe.directory <path>`: Whitelist multi-user directories to allow Git inspection across mismatched UIDs.
- `git log -p`: Display full commit history along with unified diff patch contents.
- `cat /var/run/secrets/kubernetes.io/serviceaccount/token`: Default Kubernetes pod service account token location.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Superficial Redaction Does Not Purge Git History:** Modifying sensitive files in subsequent commits leaves raw data intact within historical Git snapshots. True remediation requires history rewriting tools (`git filter-repo`, BFG Repo-Cleaner) and immediate credential rotation.
2. **Repository Permissions & Multi-User Risks:** Shared repositories on multi-user servers must restrict read/write access to `.git/` directories to prevent both information disclosure and privilege escalation via malicious hook scripts.
3. **Decoy / Canary Tokens for Detection:** Deploying obvious honeypot tokens in standard cloud/K8s paths helps security operations centers (SOC) detect unauthorized discovery activities early.
