# BreachLab - Ghost Track: Level 12 → 13 (Key Not Password)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 12 → 13 (Key Not Password)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost12`
- **Goal:** Authenticate and log in as `ghost13` using SSH Private Key Authentication
- **Next Connection:** `ssh -i sshkey.private ghost13@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

Transitioning away from password-based authentication, analyst **Kael** configured public-key cryptography for subsequent sessions ("There is no password for the next level. There's a private key instead."). The objective is to identify the SSH private key stored in the user directory, verify its permissions, and use it to authenticate as `ghost13`.

---

## 2. Reconnaissance & Artifact Inspection

Logging in via SSH as `ghost12` and inspecting directory contents:

```bash
ghost12@breachlab:~$ ls -la
total 64
drwx------ 1 ghost12 ghost12 4096 Jun  2 20:32 .
drwxr-xr-x 1 root    root    4096 May 19 12:05 ..
-rw-r--r-- 1 ghost12 ghost12  220 Jan  6  2022 .bash_logout
-rw-r--r-- 1 ghost12 ghost12 3771 Jan  6  2022 .bashrc
drwx------ 2 ghost12 ghost12 4096 Jun  1 04:55 .cache
-rw-r--r-- 1 ghost12 ghost12  807 Jan  6  2022 .profile
drwx------ 2 ghost12 ghost12 4096 May 31 10:06 .ssh
-rw------- 1 ghost12 ghost12  411 May 19 12:05 sshkey.private
-rw-r--r-- 1 ghost12 ghost12  102 May 19 12:05 sshkey.private.pub
```

### Artifact Findings

- `sshkey.private`: OpenSSH/Ed25519/RSA private key file with proper restrictive permissions (`600` / `-rw-------`).
- `sshkey.private.pub`: Corresponding public key intended to reside in the target user's `~/.ssh/authorized_keys`.

---

## 3. SSH Key Authentication & Target Access

Using the private key with the `-i` (identity file) option to authenticate directly into `ghost13`:

```bash
ghost12@breachlab:~$ ssh -i sshkey.private ghost13@localhost -p 2222
# Or connecting from the attacking machine:
ssh -i sshkey.private ghost13@204.168.229.209 -p 2222
```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost13` |
| **Authentication Method** | SSH Private Key Authentication (`-i`) |
| **Flag** | `K3y_N0t_P4ss` |
| **Identity File** | `sshkey.private` |
| **Target SSH Command** | `ssh -i sshkey.private ghost13@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `ssh -i <private_key_file> <user>@<host> -p <port>`: Authenticate to an SSH server using an identity (private key) file instead of password prompts.
- `chmod 600 <key_file>`: Ensure private key files are strictly readable/writable only by the owner (OpenSSH clients will reject keys with permissive access permissions like `644` or `777`).
- `ssh-keygen -l -f <key_file>`: Display fingerprint and key algorithm information.

---

## 6. Lessons Learned

1. **Public-Key Cryptography in SSH:** Public keys are stored on the server (`~/.ssh/authorized_keys`), while the matching private key never leaves the client/user possession.
2. **File Permission Strictness:** SSH clients strictly enforce permissions on private keys; any key with group or other read permissions will trigger an `UNPROTECTED PRIVATE KEY FILE!` warning and abort the connection.
