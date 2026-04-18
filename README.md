# CyberSecurity Repository

This repository contains write-ups, scripts, and tools from practicing penetration testing on TryHackMe and similar platforms.

## Structure

```
~/CyberSecurity/
├── README.md                    # This file
├── THM/                       # TryHackMe challenges
│   ├── AGENTS.md              # OpenCode agents configuration
│   ├── new_room.sh           # Script to create new room directories
│   ├── Blue/                # Windows machine (EternalBlue)
│   ├── Team/               # Linux machine (LFI + Privesc)
│   ├── The-Game/           # Malware/RE challenge
│   ├── W1seGuy/           # Crypto challenge
│   └── Authentication-Bypass/
```

---

## Methodology

This repository follows the PTES (Penetration Testing Execution Standard) methodology:

1. **RECONNAISSANCE** - Passive/active information gathering
2. **SCANNING** - Port scanning, service enumeration
3. **ENUMERATION** - Users, shares, directories, subdomains
4. **EXPLOITATION** - Vulnerabilities, initial access
5. **POST-EXPLOITATION** - Privilege escalation, pivoting
6. **REPORTING** - Full documentation

---

## Challenges Completed

### 1. Blue (Windows)

**Room:** TryHackMe - Blue  
**Target:** 10.65.163.160  
**Platform:** Windows 7 Professional SP1 x64

**Summary:**
- Windows 7 machine with SMB exposure
- Vulnerable to MS17-010 (EternalBlue)
- Exploited using Metasploit module `exploit/windows/smb/ms17_010_eternalblue`
- Gained direct SYSTEM access
- Extracted local hashes with `hashdump`
- Cracked Jon's password using John the Ripper

**Flags Found:**
- `flag1{access_the_machine}` - C:\flag1.txt
- `flag2{sam_database_elevated_access}` - C:\Windows\System32\config\flag2.txt
- `flag3{admin_documents_can_be_valuable}` - C:\Users\Jon\Documents\flag3.txt

**Tools Used:**
- nmap with smb-vuln-ms17-010 script
- Metasploit (msfconsole)
- John the Ripper for hash cracking

---

### 2. Team (Linux)

**Room:** TryHackMe - Team  
**Target:** 10.65.164.232  
**Platform:** Linux (Ubuntu)

**Summary:**
- Multiple services: FTP (21), SSH (22), HTTP (80)
- Virtual hosts: team.thm, dev.team.thm
- Discovered Local File Inclusion (LFI) vulnerability on dev.team.thm
- Exploited LFI to read /etc/passwd and user flag
- Found SSH private key in sshd_config comments via LFI
- SSH as user `dale` using recovered key
- Privilege escalation: dale -> gyles (sudo) -> root (writable cron script)

**Flags Found:**
- User: `THM{6Y0TXHz7c2d}` (via LFI as dale)
- Root: `THM{fhqbznavfonq}` (via writable cron script)

**Vulnerabilities:**
- Local File Inclusion (LFI) via Path Traversal
- Information Disclosure (SSH private key in config)
- sudo misconfiguration
- Writable cron script

**Tools Used:**
- nmap, gobuster, nikto
- ffuf for vhost fuzzing
- curl for LFI exploitation
- hydra for password attacks

---

### 3. The-Game (Malware/RE)

**Room:** TryHackMe - The-Game  
**Target:** Tetrix.exe (Binary Analysis Challenge)

**Summary:**
- PE32+ executable (Windows GUI app)
- Built with Godot Engine 4.x
- Embedded game resources within binary
- Decoy data: ESP32 firmware images
- Flag found embedded in plaintext near EOF

**Flag Found:**
- `THM{I_CAN_READ_IT_ALL}` (at offset 93001116)

**Tools Used:**
- file, strings
- binwalk
- grep/xxd for hex analysis
- Python for pattern matching

---

### 4. W1seGuy (Crypto)

**Room:** TryHackMe - W1seGuy  
**Challenge:** XOR Encryption

**Summary:**
- Server provides XOR-encrypted flag
- First 4 bytes known: "THM{"
- Used chosen-plaintext attack to recover key
- Bruteforced remaining key characters
- Submitted key for second flag

**Solution:** Python script using XOR chosen-plaintext attack

---

### 5. Authentication-Bypass

**Room:** TryHackMe  
**Challenge:** Username Enumeration

**Summary:**
- Valid usernames discovered via enumeration
- Results saved in valid_usernames.txt

---

## Tools & Scripts

### new_room.sh

Script to create organized room directories with report templates:

```bash
./THM/new_room.sh <room_name> [target_ip]
```

Creates:
- Room directory with report template
- Skill file for pentesting methodology

---

## OpenCode Agents

The repository includes 6 specialized pentesting agents:

1. **recon.md** - OSINT/reconnaissance
2. **scanner.md** - Port scanning (nmap)
3. **web.md** - Web enumeration (gobuster, ffuf, nikto)
4. **exploit.md** - Exploitation (Metasploit, reverse shells)
5. **privesc.md** - Privilege escalation
6. **cracker.md** - Hash cracking (john, hashcat, hydra)

Each agent follows PTES methodology and documents findings in report files.

---

## Common Commands

### Port Scanning
```bash
nmap -sV -sC -T4 -oN nmap_initial.txt <IP>
nmap -p- --min-rate 5000 -T4 -oN nmap_full.txt <IP>
nmap -sU --top-ports 20 -oN nmap_udp.txt <IP>
```

### Web Enumeration
```bash
gobuster dir -u http://<IP> -w wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html
ffuf -w wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://<IP> -H "Host: FUZZ.<domain>"
nikto -h http://<IP>
```

### Privilege Escalation
```bash
# Linux
sudo -l
find / -perm -4000 2>/dev/null
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh

# Windows
.\winPEAS.exe
whoami /priv
```

### Hash Cracking
```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
hashcat -m <mode> hash.txt wordlists/rockyou.txt
hydra -l <user> -P wordlists/rockyou.txt <IP> ssh
```

---

## Wordlists

```
/usr/share/wordlists/rockyou.txt
/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

---

## Golden Rules

- Always save command output to files (-oN filename.txt)
- Use `-Pn` when ICMP is blocked
- Stabilize shells: `python3 -c 'import pty;pty.spawn("/bin/bash")'`
- When credentials found, try on ALL services
- Check source code, cookies, HTTP headers for web apps
- Document everything in report files

---

## License

This repository is for educational purposes. All targets are in controlled lab environments (TryHackMe, HackTheBox, CTFs).