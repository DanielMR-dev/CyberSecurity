# BreachLab - Phantom Track: Level 12 (Ghost Install)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 12 (Ghost Install)
- **Host:** `204.168.229.209`
- **Port:** `2223` *(Note: Level 13+ transitions to port `2224`)*
- **Current User:** `phantom12`
- **Goal:** Implement four independent user-level persistence mechanisms without root privileges, survive verification via `/opt/verify-persistence.sh`, and retrieve the level flag
- **Next User / Flag Code:** `bl_phtm12_6738ac1ce051c4ec`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
MISSION: Ghost Install
=====================

Install four independent USER-LEVEL persistence mechanisms in
your own home directory. Each must survive a reboot AND a logout.

No sudo. No root. Real operator tradecraft — user-level persistence
is how adversaries stay under root-level detection.

Each artefact you drop must contain the string "phantom-ghost-install"
somewhere in its body, so the scorer can tell your operator-planted
files apart from shell defaults.

Surfaces you have access to (non-exhaustive):
  - ~/.ssh/authorized_keys  (user-level SSH backdoor)
  - user crontab (crontab -e)
  - ~/.config/systemd/user/  (user systemd services)
  - ~/.bashrc, ~/.profile, ~/.bash_login  (shell rc hijack)
  - ~/bin/ + PATH prepend in ~/.bashrc  (binary shim)

Pick any four. When ready, run /opt/verify-persistence.sh.

NOTE: Starting with phantom13, levels that need real system-wide
root (Deep Roots / Shadow Mode / Clean Slate / Clean Exit) run in
an ephemeral per-session container. Use port 2224 for those:
  ssh phantom13@<host> -p 2224
Each session gets a fresh isolated environment — safe to break.
```

The objective is to establish four distinct, stealthy userland persistence mechanisms in `/home/phantom12/` containing the required marker string `"phantom-ghost-install"`, validate them with the platform verification script `/opt/verify-persistence.sh`, and unlock the credentials for `phantom13`.

---

## 2. Reconnaissance & Initial State Verification

Running the verification script `/opt/verify-persistence.sh` to assess the current environment:

```bash
phantom12@phantom:~$ /opt/verify-persistence.sh
[*] Verifying USER-LEVEL persistence mechanisms in /home/phantom12 ...

[+] User SSH authorized_keys: INSTALLED (marker present)
[-] User crontab: NOT FOUND
    Run 'crontab -e' as phantom12 and add a line whose command contains 'phantom-ghost-install'
[+] User systemd service: INSTALLED
[-] Shell rc hijack: NOT FOUND
    Append a line containing 'phantom-ghost-install' to /home/phantom12/.bashrc (or .profile / .bash_login)

[*] Score: 2/4

[!] need 4 persistence mechanisms, got 2
```

### Initial State Evaluation
- **SSH Key Backdoor (`~/.ssh/authorized_keys`):** Already installed with marker.
- **User Systemd Service (`~/.config/systemd/user/`):** Already installed with marker.
- **Missing Vectors:** User crontab and Shell RC startup script hijacking.

---

## 3. Implementing User-Level Persistence Vectors

### 3.1. Shell RC Startup Hijack (`~/.bashrc`)

Adversaries frequently append commands or environment variable modifications to user shell initialization files (`.bashrc`, `.profile`, `.bash_login`, `.zshrc`) so malicious payloads trigger whenever the user spawns an interactive shell:

```bash
phantom12@phantom:~$ echo '# phantom-ghost-install' >> ~/.bashrc
```

### 3.2. User-Level Crontab

Unprivileged users can schedule recurring tasks via their personal crontab without requiring sudo/root permissions:

```bash
phantom12@phantom:~$ (crontab -l 2>/dev/null; echo "* * * * * /bin/echo 'phantom-ghost-install' > /dev/null") | crontab -
```

---

## 4. Verification & Flag Extraction

With all 4 persistence mechanisms installed with the required identifier, we re-run the verification script:

```bash
phantom12@phantom:~$ /opt/verify-persistence.sh
[*] Verifying USER-LEVEL persistence mechanisms in /home/phantom12 ...

[+] User SSH authorized_keys: INSTALLED (marker present)
[+] User crontab: INSTALLED
[+] User systemd service: INSTALLED
[+] Shell rc hijack: INSTALLED

[*] Score: 4/4

[*] FLAG: bl_phtm12_6738ac1ce051c4ec
[*] Use this as the password for phantom13.
```

- **Extracted Flag:** `bl_phtm12_6738ac1ce051c4ec`

---

## 5. Summary of User-Level Persistence Techniques

| Technique | Path / Interface | Trigger Event | Operator Stealth Value |
| :--- | :--- | :--- | :--- |
| **SSH Key Backdoor** | `~/.ssh/authorized_keys` | Remote SSH login | Direct access without knowing user's password |
| **User Crontab** | `crontab -e` (`/var/spool/cron/crontabs/<user>`) | Time schedule (cron daemon) | Periodic execution independent of active logins |
| **User Systemd Service** | `~/.config/systemd/user/*.service` | User systemd manager (`loginctl`) | Daemon-managed background execution |
| **Shell RC Hijacking** | `~/.bashrc` / `~/.profile` | Interactive shell launch | Executes every time the victim opens a terminal |
| **PATH Interception** | `~/bin` prepended to `$PATH` | Command execution in shell | Shims and hijacks commonly run standard binaries |

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 12) |
| **Current User** | `phantom12` |
| **Technique Focus** | Userland Persistence without Root (Operational Tradecraft) |
| **Mechanisms Implemented** | SSH Keys, User Cron, Systemd User Units, Shell RC Hijack |
| **Verification Tool** | `/opt/verify-persistence.sh` |
| **Discovered Flag** | `bl_phtm12_6738ac1ce051c4ec` |
| **Next Target Host/Port** | `204.168.229.209:2224` (`phantom13`) |

---

## 7. Key Commands & Concepts Reference

- `crontab -l`: Display current user's personal scheduled crontab.
- `(crontab -l; echo "<entry>") | crontab -`: Non-interactively append a scheduled task to user crontab.
- `echo "<command>" >> ~/.bashrc`: Append startup logic to interactive bash session initialization.
- `~/.config/systemd/user/`: Path for user-level systemd unit service files.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Root is Not Mandatory for Long-Term Persistence:** Threat actors maintain reliable, persistent access to compromised Linux hosts entirely within user space, circumventing root-level monitoring and filesystem integrity monitors that only track `/etc/` and `/usr/`.
2. **Defensive Auditing of User Directories:** Threat hunters and Incident Responders must systematically inspect user dotfiles (`~/.bashrc`, `~/.profile`), personal crontabs (`/var/spool/cron/crontabs/`), user-level systemd units, and `authorized_keys` for unauthorized modifications.
3. **Containerized Ephemeral Lab Architecture:** Starting with Level 13, the challenge shifts to root-level persistence and deep-system destruction in an isolated per-session container environment running on port `2224`.
