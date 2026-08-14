# BreachLab - Ghost Track: Level 13 → 14 (Port 30000)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 13 → 14 (Port 30000)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost13`
- **Goal:** Retrieve the password / credentials for `ghost14`
- **Next Connection:** `ssh ghost14@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

The level instructions state:
> *"A service on port 30000 will trade the next password for the current one. Hand-craft the conversation. No browser. No client library."*

The objective is to retrieve the current level's password/token stored locally in the home directory (`flag`), establish a raw TCP connection to the local listener running on port `30000` using Netcat (`nc`), transmit the token, and obtain the password for `ghost14`.

---

## 2. Reconnaissance & Artifact Inspection

Logging in via SSH as `ghost13` and inspecting the directory structure:

```bash
ghost13@breachlab:~$ ls -la
total 60
drwx------ 1 ghost13 ghost13 4096 Jun  2 20:45 .
drwxr-xr-x 1 root    root    4096 May 19 12:05 ..
-rw-r--r-- 1 ghost13 ghost13  220 Jan  6  2022 .bash_logout
-rw-r--r-- 1 ghost13 ghost13 3771 Jan  6  2022 .bashrc
drwx------ 2 ghost13 ghost13 4096 Jun  1 06:34 .cache
-rw-r--r-- 1 ghost13 ghost13  807 Jan  6  2022 .profile
drwx------ 1 ghost13 ghost13 4096 May 20 19:25 .ssh
-r-------- 1 ghost13 ghost13   13 May 19 12:05 flag
```

### Reading Local Current Flag / Token

```bash
ghost13@breachlab:~$ cat flag
K3y_N0t_P4ss
```

The file `flag` contains `K3y_N0t_P4ss`, which serves as the current stage key/password required by the authentication daemon on port `30000`.

---

## 3. Network Service Interaction & Password Retrieval

We connect directly to the service listening on `localhost:30000` using `nc` (Netcat) and pipe the current flag into the TCP socket:

```bash
ghost13@breachlab:~$ echo "K3y_N0t_P4ss" | nc localhost 30000
Correct! Next password: N3tc4t_D3l1v3r
```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost14` |
| **Password / Flag** | `N3tc4t_D3l1v3r` |
| **Target Service** | `localhost:30000` |
| **Submission Payload** | `K3y_N0t_P4ss` |
| **Target SSH Command** | `ssh ghost14@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `nc localhost <port>`: Open a raw TCP connection to a local port without requiring higher-level client libraries or browsers.
- `echo "<data>" | nc localhost <port>`: Send data directly through a standard input stream to a listening network service and receive the server response.
- `cat flag | nc localhost 30000`: Pipe file contents directly to a local socket.

---

## 6. Lessons Learned

1. **Direct Socket Communication:** Lightweight command-line networking utilities like `nc` allow fast, automated interaction with raw TCP/UDP socket listeners without needing bloated HTTP or high-level application layer clients.
2. **Token Exchange Protocol:** Many CTF and wargame challenges utilize custom daemon services that validate possession of the current stage's secret before returning the subsequent credential.
