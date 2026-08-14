# BreachLab - Ghost Track: Level 17 → 18 (No Shell For You)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 17 → 18 (No Shell For You)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost17`
- **Goal:** Retrieve the password / credentials for `ghost18`
- **Next Connection:** `ssh ghost18@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

The MOTD banner for Level 17 describes a restricted login environment:
> *"Log in and get kicked. The server runs a startup script that boots you on arrival. Read a file without ever getting an interactive shell."*

Whenever an interactive TTY SSH session is initialized, a startup profile script (`.force-logout` invoked via `.bashrc`) terminates the connection immediately. The objective is to bypass interactive shell startup scripts by executing remote commands directly through the SSH client invocation to read the `flag` file.

---

## 2. Reconnaissance & Shell Restriction Analysis

Attempting a standard interactive SSH login results in immediate session disconnection:

```bash
$ ssh ghost17@204.168.229.209 -p 2222
(ghost17@204.168.229.209) Password:
...
Connection closed. No interactive shell.
Connection to 204.168.229.209 closed.
```

---

## 3. Remote Command Execution via SSH

SSH allows clients to specify a command string at the end of the connection syntax. When a remote command is supplied, SSH executes the binary directly in a non-interactive subshell without spawning an interactive login shell or invoking interactive login scripts (e.g., `.bashrc` logout hooks).

### Inspecting Remote Files

```bash
$ ssh ghost17@204.168.229.209 -p 2222 ls -la
(ghost17@204.168.229.209) Password:
total 64
drwx------ 1 ghost17 ghost17 4096 Jun  1 04:01 .
drwxr-xr-x 1 root    root    4096 May 19 12:05 ..
-rw-r--r-- 1 ghost17 ghost17  220 Jan  6  2022 .bash_logout
-rw-r--r-- 1 ghost17 ghost17 3867 May 19 12:05 .bashrc
drwx------ 2 ghost17 ghost17 4096 Jun  1 04:01 .cache
-rwxr-xr-x 1 ghost17 ghost17   65 May 19 12:05 .force-logout
-rw-r--r-- 1 ghost17 ghost17  807 Jan  6  2022 .profile
drwx------ 2 ghost17 ghost17 4096 May 19 14:24 .ssh
-r-------- 1 ghost17 ghost17   13 May 19 12:05 flag
```

### Reading the Flag File

```bash
$ ssh ghost17@204.168.229.209 -p 2222 cat flag
(ghost17@204.168.229.209) Password:
Sh3ll_D3n13d
```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost18` |
| **Password / Flag** | `Sh3ll_D3n13d` |
| **Restriction Mechanism** | `.force-logout` on interactive login |
| **Bypass Method** | Non-interactive SSH command execution (`ssh ... cat flag`) |
| **Target SSH Command** | `ssh ghost18@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `ssh <user>@<host> -p <port> <command>`: Execute an arbitrary remote command over SSH non-interactively without allocating a TTY or launching interactive shell configuration files.
- `ssh -T <user>@<host>`: Explicitly disable pseudo-terminal allocation.
- `ssh <user>@<host> /bin/sh`: Force an alternate shell binary or bypass forced `.bashrc` profile actions if permitted.

---

## 6. Lessons Learned

1. **Interactive vs Non-Interactive SSH Execution:** Startup files such as `.bashrc` or `.profile` can contain custom exit traps or force-logout scripts intended to deny interactive access, but direct SSH command execution bypasses these shell initialization routines.
2. **True Shell Restrictions:** To securely restrict an account to no interactive shell, the server configuration must enforce a restricted shell (such as `/sbin/nologin`, `/bin/false`, `rssh`, or `ForceCommand` in `sshd_config`) rather than relying on user-writable or userland profile scripts.
