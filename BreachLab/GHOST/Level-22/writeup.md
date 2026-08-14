# BreachLab - Ghost Track: Level 22 (Graduation / Multi-Shard Convergence)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 22 · CLASSIFIED (Graduation)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost22`
- **Goal:** Claim the Ghost Track Graduation Flag
- **Gatekeeper Service:** `localhost:31339`

---

## 1. Scenario & Objectives

The MOTD banner and `BRIEFING` document the graduation trial:
> *"Twenty-two levels behind you. One classified file left on this machine — split into three shards, each guarded by a different technique from the track.*
> - *Shard 1 — buried in a binary blob*
> - *Shard 2 — encoded for transport*
> - *Shard 3 — guarded by a SUID helper*
>
> *Recover all three. Hand them to the gatekeeper listening on TCP :31339. Format (exact):*
> `SHARD1:<val>|SHARD2:<val>|SHARD3:<val>`"

---

## 2. Reconnaissance & Artifact Inspection

Logging in via SSH as `ghost22` and listing directory contents:

```bash
ghost22@breachlab:~$ ls -la
total 80
drwx------ 1 ghost22 ghost22 4096 Jun  2 18:54 .
drwxr-xr-x 1 root    root    4096 May 19 12:05 ..
...
-rw-r----- 1 ghost22 ghost22  343 May 19 12:05 BRIEFING
-rw-r----- 1 ghost22 ghost22 8215 May 19 12:05 relic.bin
-rw-r----- 1 ghost22 ghost22   25 May 19 12:05 scroll.b64
```

### Inspecting `BRIEFING`

```bash
ghost22@breachlab:~$ cat BRIEFING
GRADUATION — OPERATIVE BRIEFING
================================

Three shards are scattered across this machine.
Each requires a different technique from the 22 levels behind you.

Recover all three. Combine them. Submit to the gatekeeper.

Gatekeeper: TCP localhost:31339
Format (exact): SHARD1:<val>|SHARD2:<val>|SHARD3:<val>

KAEL, out.
```

---

## 3. Shard Recovery

### Shard 1: Static Binary Analysis (`relic.bin`)

Using `strings` to extract ASCII strings from the binary blob:

```bash
ghost22@breachlab:~$ strings relic.bin | grep "SHARD"
::SHARD1:ALPHA_Z3R0::
```

- **Shard 1 Value:** `ALPHA_Z3R0`

---

### Shard 2: Base64 Payload Decoding (`scroll.b64`)

Decoding `scroll.b64` with `base64 -d`:

```bash
ghost22@breachlab:~$ cat scroll.b64 | base64 -d
SHARD2:BR4V0_0N3
```

- **Shard 2 Value:** `BR4V0_0N3`

---

### Shard 3: Privileged SUID Helper Execution (`ghost-archivist`)

During the SUID enumeration performed in Level 18, a binary `/usr/local/bin/ghost-archivist` was discovered with ownership `root:ghost22` and permissions `-rwsr-x---`. Now authenticated as `ghost22`, we execute it:

```bash
ghost22@breachlab:~$ /usr/local/bin/ghost-archivist
SHARD3:CH4RL13_TW0
```

- **Shard 3 Value:** `CH4RL13_TW0`

---

## 4. Gatekeeper Submission & Graduation Flag

With all three shards retrieved, we compile the final verification payload:
```text
SHARD1:ALPHA_Z3R0|SHARD2:BR4V0_0N3|SHARD3:CH4RL13_TW0
```

Connecting to the Gatekeeper daemon on `localhost:31339` with `nc`:

```bash
ghost22@breachlab:~$ nc localhost 31339
Ghost Graduation Gatekeeper
===========================
Submit three shards in one line, pipe-separated, no spaces:
  SHARD1:<val>|SHARD2:<val>|SHARD3:<val>

> SHARD1:ALPHA_Z3R0|SHARD2:BR4V0_0N3|SHARD3:CH4RL13_TW0

VERIFIED. All three shards accepted.
GRADUATION FLAG: Gh0st_0p3r4t1v3
```

---

## 5. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Ghost Track (Final Level 22) |
| **Shard 1** | `ALPHA_Z3R0` (`strings relic.bin`) |
| **Shard 2** | `BR4V0_0N3` (`base64 -d scroll.b64`) |
| **Shard 3** | `CH4RL13_TW0` (`/usr/local/bin/ghost-archivist`) |
| **Gatekeeper Submission** | `SHARD1:ALPHA_Z3R0\|SHARD2:BR4V0_0N3\|SHARD3:CH4RL13_TW0` |
| **Graduation Flag** | `Gh0st_0p3r4t1v3` |

---

## 6. Key Techniques Reference

- `strings <binary>`: Extract printable ASCII character sequences from raw data files.
- `base64 -d <file>`: Decode standard Base64 transport encoding.
- `/usr/local/bin/<suid_binary>`: Execute group-restricted SUID utilities to obtain root/elevated data.
- `nc localhost <port>`: Interact with local TCP daemons for challenge gatekeeper validation.

---

## 7. Track Summary & Milestone

The Ghost Track covered fundamental Linux systems, networking, cryptography, and defensive mechanics:
- File system enumeration, permissions, ACLs, and tricky shell quoting.
- Memory forensics (`/proc/<pid>/environ`), process inspection, and environment variables.
- Raw network socket communications over plain TCP (`nc`) and encrypted TLS (`openssl s_client`).
- Automated Bash scripting and brute forcing.
- Scheduled task / Cron race condition exploitation.
- Git repository forensics and historical commit inspection.
- SetUID binary privilege escalation.
