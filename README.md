# CyberSecurity Repository

This repository contains write-ups, scripts, and tools from practicing penetration testing on TryHackMe and similar platforms.

## Structure

```
~/CyberSecurity/
├── README.md                    # This file
├── BreachLab/                  # BreachLab wargames
│   ├── GHOST/                  # Ghost Track
│   │   └── Level-00/           # Level 0 → 1 (First Contact)
│   └── PHANTOM/                # Phantom Track
└── THM/                        # TryHackMe challenges
    ├── AGENTS.md               # OpenCode agents configuration
    ├── new_room.sh             # Script to create new room directories
    ├── Blue/                   # Windows machine (EternalBlue)
    ├── Team/                   # Linux machine (LFI + Privesc)
    ├── The-Game/               # Malware/RE challenge
    ├── W1seGuy/                # Crypto challenge
    └── Authentication-Bypass/  # Web auth bypass
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

## Challenge Progress Tracker

| Challenge / Room | Platform | Target / OS | Focus / Vulnerability | Status | Write-up / Evidence |
| :--- | :---: | :---: | :--- | :---: | :--- |
| [**Ghost - Level 00**](./BreachLab/GHOST/Level-00/) | BreachLab | Linux Wargame | Linux CLI Basics (`ls`, `cat`, `cd`) & Artifact Discovery | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-00/writeup.md) |
| [**Blue**](./THM/Blue/) | TryHackMe | Windows 7 SP1 | MS17-010 (EternalBlue) & SAM Cracking | `🟢 Completed` | [writeup.md](./THM/Blue/writeup.md) |
| [**Team**](./THM/Team/) | TryHackMe | Linux (Ubuntu) | LFI / VHost / Sudo & Writable Cron Privesc | `🟢 Completed` | [writeup.md](./THM/Team/writeup.md) |
| [**The-Game**](./THM/The-Game/) | TryHackMe | Binary (Godot) | Malware Analysis / RE / Plaintext Flag | `🟢 Completed` | [writeup.md](./THM/The-Game/writeup.md) |
| [**W1seGuy**](./THM/W1seGuy/) | TryHackMe | Crypto | XOR Cipher Known-Plaintext Attack | `🟢 Completed` | [writeup.md](./THM/W1seGuy/writeup.md) |
| [**Authentication-Bypass**](./THM/Authentication-Bypass/) | TryHackMe | Web App | Username Enumeration & Auth Bypass | `🟢 Completed` | [writeup.md](./THM/Authentication-Bypass/writeup.md) |

> **Status Legend:** `🟢 Completed` · `🟡 In Progress` · `⚪ Pending`

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

## License

This repository is for educational purposes. All targets are in controlled lab environments (TryHackMe, HackTheBox, CTFs).