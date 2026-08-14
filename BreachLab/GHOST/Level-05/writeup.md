# BreachLab - Ghost Track: Level 5 → 6 (The Listener)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 5 → 6 (The Listener)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost5`
- **Goal:** Retrieve the password / credentials for `ghost6`
- **Next Connection:** `ssh ghost6@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

Analyst **Kael** shifted from storing credentials on disk to hosting an in-memory network service across multiple local ports. Furthermore, standard network enumeration utilities like `ss` and `netstat` were restricted. The objective is to perform a local TCP port sweep using `nc` (Netcat), interact with discovered services, solve the two-channel authentication handshake, and extract the password for `ghost6`.

---

## 2. Reconnaissance & Initial Notes

Logging into the `ghost5` session and inspecting the home directory:

```bash
ghost5@breachlab:~$ ls -la
total 60
drwx------ 1 ghost5 ghost5 4096 Jun  4 12:20 .
drwxr-xr-x 1 root   root   4096 May 19 12:05 ..
...
-rw-r----- 1 root   ghost5  505 May 15 21:25 README
```

### Inspecting `README`

```bash
ghost5@breachlab:~$ cat README
ANALYST WORKSTATION — KAEL
Last active: 2026-03-28 02:47 UTC
Status: Abandoned

I left a service running on this box. Used to be my back channel —
two ports, one tells you how to talk, the other answers if you say
the right word.

I locked down `ss` and `netstat` weeks ago. Don't bother. The kernel
won't help you here. You'll have to knock on doors yourself.

`nc` and `curl` are still on the box. That's all you need.

Find the listener. Read what it tells you. Then answer it correctly.

— KAEL
```

---

## 3. Local Port Scanning & Service Interrogation

### Local Port Sweep with Netcat

Because `netstat` and `ss` are restricted, a port scan was executed locally across the full port range using `nc -zv`:

```bash
ghost5@breachlab:~$ nc -zv localhost 1-65535 2>&1 | grep -E "succeeded|open"
Connection to localhost (::1) 22 port [tcp/ssh] succeeded!
Connection to localhost (127.0.0.1) 30000 port [tcp/*] succeeded!
Connection to localhost (127.0.0.1) 30001 port [tcp/*] succeeded!
Connection to localhost (127.0.0.1) 30002 port [tcp/*] succeeded!
Connection to localhost (127.0.0.1) 30100 port [tcp/*] succeeded!
Connection to localhost (127.0.0.1) 30101 port [tcp/*] succeeded!
Connection to localhost (127.0.0.1) 31339 port [tcp/*] succeeded!
Connection to localhost (127.0.0.1) 31790 port [tcp/*] succeeded!
Connection to localhost (127.0.0.1) 39892 port [tcp/*] succeeded!
Connection to localhost (127.0.0.1) 41337 port [tcp/*] succeeded!
```

### Interrogating Open Ports

A shell loop was used to banner grab across all listening ports:

```bash
ghost5@breachlab:~$ for port in 30000 30001 30002 30100 30101 31339 31790 39892 41337; do
    echo -e "\n=== Interrogating Port $port ==="
    nc -w 2 localhost $port
done
```

#### Port 30100 (Informational Channel A)
```text
  GHOST PROTOCOL — CHANNEL A
  ─────────────────────────────────────

  This channel is informational only.

  Authentication token: GHOST
  Secure channel: port 30101

  Send the token to receive your credential.
```

#### Port 30101 (Authentication Channel B)
```text
AUTHENTICATE:
```

#### Port 31339 (Ghost Graduation Gatekeeper)
```text
Ghost Graduation Gatekeeper
===========================
Submit three shards in one line, pipe-separated, no spaces:
  SHARD1:<val>|SHARD2:<val>|SHARD3:<val>
```

#### Port 41337 (Bonus Easter Egg - Phantom Track Preview)
```text
  [ CLASSIFIED — GHOST TRACK BONUS ]
  ───────────────────────────────────────────
  OPERATIVE KAEL — STATUS: ACTIVE
  Last known location: PHANTOM network.
  "The real breach starts in the pipeline. Docker. Kubernetes. GitHub Actions."
  NEXT TRACK: PHANTOM (30 levels of Linux privesc).
```

---

## 4. Authentication & Flag Extraction

Sending the authentication token `GHOST` discovered on port `30100` directly into the secure listener on port `30101`:

```bash
ghost5@breachlab:~$ echo "GHOST" | nc localhost 30101
AUTHENTICATE:
  Credential: P0rts_N3v3r_L13
```

---

## 5. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost6` |
| **Password / Flag** | `P0rts_N3v3r_L13` |
| **Listening Ports** | `30100` (Token info) / `30101` (Auth prompt) |
| **Target SSH Command** | `ssh ghost6@204.168.229.209 -p 2222` |

---

## 6. Key Commands Reference

- `nc -zv localhost 1-65535`: Port scan local TCP services when administrative sockets tools (`ss`, `netstat`, `lsof`) are restricted.
- `nc -w 2 localhost <port>`: Connect and banner-grab from a target socket with a timeout.
- `echo "<payload>" | nc localhost <port>`: Send automated strings or tokens through a TCP stream.

---

## 7. Lessons Learned

1. **Host-Based Port Sweeping:** When native kernel socket diagnostic commands (`ss`, `netstat`) are disabled or stripped of execution permissions, userland tools like Netcat (`nc`) or Bash's `/dev/tcp` pseudo-device can perform port discovery.
2. **Two-Tier Service Handshakes:** Network authentication services often separate broadcast/discovery endpoints from authenticated data transmission ports.
