# CyberSecurity Repository

This repository contains write-ups, scripts, and tools from practicing penetration testing on TryHackMe and similar platforms.

## Structure

```
~/CyberSecurity/
├── README.md                    # This file
├── BreachLab/                  # BreachLab wargames
│   ├── GHOST/                  # Ghost Track
│   │   ├── Level-00/           # Level 0 → 1 (First Contact)
│   │   ├── Level-01/           # Level 1 → 2 (Name Game)
│   │   ├── Level-02/           # Level 2 → 3 (In The Shadows)
│   │   ├── Level-03/           # Level 3 → 4 (Access Denied)
│   │   ├── Level-04/           # Level 4 → 5 (Signal in the Noise)
│   │   ├── Level-05/           # Level 5 → 6 (The Listener)
│   │   ├── Level-06/           # Level 6 → 7 (Ghost in the Machine)
│   │   ├── Level-07/           # Level 7 → 8 (Lost in Translation)
│   │   ├── Level-08/           # Level 8 → 9 (Something's Running)
│   │   ├── Level-09/           # Level 9 → 10 (Noise Floor)
│   │   ├── Level-10/           # Level 10 → 11 (Binary Strings)
│   │   ├── Level-11/           # Level 11 → 12 (Wrapped Three Deep)
│   │   ├── Level-12/           # Level 12 → 13 (Key Not Password)
│   │   ├── Level-13/           # Level 13 → 14 (Port 30000)
│   │   ├── Level-14/           # Level 14 → 15 (TLS, Not Plaintext)
│   │   └── Level-15/           # Level 15 → 16 (Port Range)
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
| [**Ghost - Level 01**](./BreachLab/GHOST/Level-01/) | BreachLab | Linux Wargame | Shell Quoting, Escaping & Tricky Filenames | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-01/writeup.md) |
| [**Ghost - Level 02**](./BreachLab/GHOST/Level-02/) | BreachLab | Linux Wargame | Hidden Files, Directories (`ls -la`) & Dotfile Traversal | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-02/writeup.md) |
| [**Ghost - Level 03**](./BreachLab/GHOST/Level-03/) | BreachLab | Linux Wargame | Linux Group Permissions & Access Control Lists | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-03/writeup.md) |
| [**Ghost - Level 04**](./BreachLab/GHOST/Level-04/) | BreachLab | Linux Wargame | Log Filtering, Anomaly Detection & Text Processing (`grep`) | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-04/writeup.md) |
| [**Ghost - Level 05**](./BreachLab/GHOST/Level-05/) | BreachLab | Linux Wargame | Local TCP Port Scanning & Netcat Service Handshake | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-05/writeup.md) |
| [**Ghost - Level 06**](./BreachLab/GHOST/Level-06/) | BreachLab | Linux Wargame | Environment Variables (`env`) & Base64 Decoding | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-06/writeup.md) |
| [**Ghost - Level 07**](./BreachLab/GHOST/Level-07/) | BreachLab | Linux Wargame | Multi-Stage Deobfuscation (Hexdump `xxd -r` & Base64) | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-07/writeup.md) |
| [**Ghost - Level 08**](./BreachLab/GHOST/Level-08/) | BreachLab | Linux Wargame | Process Memory Forensics & `/proc/<PID>/environ` | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-08/writeup.md) |
| [**Ghost - Level 09**](./BreachLab/GHOST/Level-09/) | BreachLab | Linux Wargame | Binary Static Analysis & ASCII Extraction (`strings`) | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-09/writeup.md) |
| [**Ghost - Level 10**](./BreachLab/GHOST/Level-10/) | BreachLab | Linux Wargame | Set Difference & Duplicate Filtering (`sort \| uniq -u`) | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-10/writeup.md) |
| [**Ghost - Level 11**](./BreachLab/GHOST/Level-11/) | BreachLab | Linux Wargame | Nested Archives & Multi-Format Decompression | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-11/writeup.md) |
| [**Ghost - Level 12**](./BreachLab/GHOST/Level-12/) | BreachLab | Linux Wargame | SSH Private Key Authentication (`ssh -i`) | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-12/writeup.md) |
| [**Ghost - Level 13**](./BreachLab/GHOST/Level-13/) | BreachLab | Linux Wargame | Local TCP Port Communication (`nc` / Netcat) | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-13/writeup.md) |
| [**Ghost - Level 14**](./BreachLab/GHOST/Level-14/) | BreachLab | Linux Wargame | TLS Encrypted Socket Communication (`openssl s_client`) | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-14/writeup.md) |
| [**Ghost - Level 15**](./BreachLab/GHOST/Level-15/) | BreachLab | Linux Wargame | Port Range Scanning (`nmap -sV`) & TLS Service Interrogation | `🟢 Completed` | [writeup.md](./BreachLab/GHOST/Level-15/writeup.md) |
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