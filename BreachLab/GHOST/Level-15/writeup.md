# BreachLab - Ghost Track: Level 15 → 16 (Port Range)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 15 → 16 (Port Range)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost15`
- **Goal:** Retrieve the password / credentials for `ghost16`
- **Next Connection:** `ssh ghost16@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

The MOTD banner for Level 15 introduces port range enumeration with TLS:
> *"One port in a range speaks TLS. The rest are closed or silent. Find the one that will greet you back."*

The objective is to scan the high port range (`30000-40000`) on `localhost` to identify which active listener speaks TLS and corresponds to Level 15. Once identified, interact with the service using `openssl s_client`, transmit the current level's password (`TLS_0r_N0th1ng`), and obtain the password for `ghost16`.

---

## 2. Reconnaissance & Service Enumeration

Logging in via SSH as `ghost15`:

```bash
ghost15@breachlab:~$ ls -la
total 48
drwx------ 1 ghost15 ghost15 4096 Jun  3 10:19 .
drwxr-xr-x 1 root    root    4096 May 19 12:05 ..
...
drwx------ 2 ghost15 ghost15 4096 May 20 19:25 .ssh
```

### Port Range Scan with Nmap Service Detection

We execute an Nmap service detection scan across ports `30000-40000`:

```bash
ghost15@breachlab:~$ nmap -sV -p 30000-40000 localhost
Starting Nmap 7.80 ( https://nmap.org ) at 2026-06-05 01:38 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00021s latency).
PORT      STATE SERVICE             VERSION
30000/tcp open  ndmps?              # Level 13 plaintext token service
30001/tcp open  ssl/pago-services1? # Level 14 TLS service
30002/tcp open  pago-services2?     # Level 19 PIN service
30100/tcp open  rwp?                # Channel A informational service
30101/tcp open  unknown             # Channel B auth prompt
31339/tcp open  unknown             # Ghost Graduation Gatekeeper
31790/tcp open  ssl/unknown         # Candidate TLS listener for Level 15
```

### Distinguishing TLS Listeners

Nmap revealed two active TLS services:
1. `30001/tcp`: Fingerprinted as the previous Level 14 service.
2. `31790/tcp`: Unidentified SSL/TLS daemon.

---

## 3. TLS Service Interrogation & Password Retrieval

### Testing Port 30001 (Level 14 Service)
Connecting to port `30001` with `openssl s_client` confirms it belongs to Level 14:

```bash
ghost15@breachlab:~$ openssl s_client -connect localhost:30001 -quiet
depth=0 CN = ghost-internal
verify return:1
Send the current level password:
TLS_0r_N0th1ng
Wrong password. (This is the Level 14 service on port 30001.)
```

### Interrogating Port 31790 (Target Level 15 Service)
Connecting to port `31790` and submitting the current token:

```bash
ghost15@breachlab:~$ openssl s_client -connect localhost:31790 -quiet
Can't use SSL_get_servername
depth=0 CN = ghost-internal
verify error:num=18:self-signed certificate
verify return:1
depth=0 CN = ghost-internal
verify return:1
Send the current level password:
TLS_0r_N0th1ng
Correct! Next password: P0rt_Sc4nn3d
```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost16` |
| **Password / Flag** | `P0rt_Sc4nn3d` |
| **Target Port** | `31790/tcp` (TLS) |
| **Submission Payload** | `TLS_0r_N0th1ng` |
| **Target SSH Command** | `ssh ghost16@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `nmap -sV -p <range> <target>`: Perform TCP port scanning with service version detection and TLS/SSL banner probing.
- `openssl s_client -connect localhost:<port> -quiet`: Establish a quiet interactive TLS stream with an SSL-wrapped network daemon.
- `echo "<password>" | openssl s_client -connect localhost:<port> -quiet`: Pipe credentials non-interactively over TLS.

---

## 6. Lessons Learned

1. **Local Port & Service Fingerprinting:** When multiple services listen on localhost, using `-sV` with Nmap rapidly distinguishes between plaintext protocols and SSL/TLS wrapped services while extracting banner fingerprints.
2. **Elimination via Service Banners:** Distinct service banners help eliminate legacy or future level listeners (e.g., ports 30000, 30001, 30002) to pinpoint the exact level daemon.
