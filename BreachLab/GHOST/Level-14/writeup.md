# BreachLab - Ghost Track: Level 14 → 15 (TLS, Not Plaintext)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 14 → 15 (TLS, Not Plaintext)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost14`
- **Goal:** Retrieve the password / credentials for `ghost15`
- **Next Connection:** `ssh ghost15@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

The MOTD banner provides the following context:
> *"Same idea as the last level — but the service now speaks TLS. Plain netcat will not work. Find a CLI that speaks TLS, and greet it right."*

Unlike Level 13 where communication was plaintext over TCP, the local daemon listening on port `30001` enforces TLS/SSL encryption. The objective is to utilize `openssl s_client` to establish an encrypted TLS socket with `localhost:30001`, provide the current level's password (`N3tc4t_D3l1v3r`), and capture the credential for `ghost15`.

---

## 2. Reconnaissance & Artifact Inspection

Logging in via SSH as `ghost14` and reviewing the home directory:

```bash
ghost14@breachlab:~$ ls -la
total 48
drwx------ 1 ghost14 ghost14 4096 Jun  1 02:07 .
drwxr-xr-x 1 root    root    4096 May 19 12:05 ..
-rw-r--r-- 1 ghost14 ghost14  220 Jan  6  2022 .bash_logout
-rw-r--r-- 1 ghost14 ghost14 3771 Jan  6  2022 .bashrc
drwx------ 2 ghost14 ghost14 4096 Jun  1 02:07 .cache
-rw-r--r-- 1 ghost14 ghost14  807 Jan  6  2022 .profile
drwx------ 2 ghost14 ghost14 4096 May 20 19:25 .ssh
```

---

## 3. Establishing TLS Connection & Password Exchange

Because the service uses TLS, standard `nc localhost 30001` will fail or hang during the handshake. We use `openssl s_client` with the `-connect` and `-quiet` flags to open an interactive TLS session:

```bash
ghost14@breachlab:~$ openssl s_client -connect localhost:30001 -quiet
Can't use SSL_get_servername
depth=0 CN = ghost-internal
verify error:num=18:self-signed certificate
verify return:1
depth=0 CN = ghost-internal
verify return:1
Send the current level password:
N3tc4t_D3l1v3r
Correct! Next password: TLS_0r_N0th1ng
```

Alternatively, this can be automated via standard input piping:

```bash
echo "N3tc4t_D3l1v3r" | openssl s_client -connect localhost:30001 -quiet
```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost15` |
| **Password / Flag** | `TLS_0r_N0th1ng` |
| **Target Service** | `localhost:30001` (TLS Encrypted) |
| **Submission Payload** | `N3tc4t_D3l1v3r` |
| **Target SSH Command** | `ssh ghost15@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `openssl s_client -connect <host>:<port>`: Command-line TLS/SSL client tool used to initiate and debug SSL/TLS connections to remote or local network servers.
- `-quiet`: Suppress diagnostic session parameters and certificate printouts, providing a clean interactive terminal stream similar to `nc`.
- `-ign_eof`: (Optional) In some cases keeps the connection open if EOF is reached.
- `socat` / `ncat --ssl`: Alternative CLI tools capable of speaking SSL/TLS when OpenSSL is not available.

---

## 6. Lessons Learned

1. **Encrypted Network Sockets:** Plaintext socket clients (such as vanilla Netcat) cannot negotiate cryptographic handshakes with TLS-wrapped endpoints.
2. **OpenSSL as an Interactive Client:** Beyond certificate generation and encryption utilities, `openssl s_client` acts as an effective Netcat equivalent for encrypted communication channels.
