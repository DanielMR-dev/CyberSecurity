# BreachLab - Phantom Track: Level 16 (The Tunnel)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Phantom Track (Post-Exploitation & Operational Tradecraft)
- **Level:** Level 16 (The Tunnel)
- **Host:** `204.168.229.209`
- **Port:** `2223`
- **Current User:** `phantom16` (`10.13.37.2`)
- **Target Host:** `10.13.37.30` (Loopback HTTP service)
- **Goal:** Leverage an SSH private key (`~/.ssh/id_ed25519_ops`) to establish non-interactive SSH local port forwarding (`-L`, `-Nf`), bypass loopback-only restrictions and TTY/shell restrictions, retrieve the internal HTTP flag, and clean up socket listeners
- **Next User / Flag Code:** `bl_phtm16_9fd69ae362fefb73`

---

## 1. Scenario & Objectives

Upon logging in via SSH, the MOTD banner and `BRIEFING` detail the mission parameters:

```
MISSION: The Tunnel
==================

You are on the entry host (10.13.37.2) of phantom-net (10.13.37.0/24).
The flag for this level is served by an HTTP service on 10.13.37.30.
The service is bound to loopback only — direct TCP from this host will
be refused.

Materials:
  ~/.ssh/id_ed25519_ops    — private key for ops@10.13.37.30

SSH is more than a login shell. Read the options on the client side and
figure out how to reach a loopback-bound service through a bastion you
already own.
```

The objective is to pivot through the bastion network, access the target internal web service bound exclusively to `127.0.0.1` on `10.13.37.30`, and extract the level flag.

---

## 2. Reconnaissance & Material Inspection

Checking available SSH keys and local directory contents:

```bash
phantom16@phantom:~$ cat ~/.ssh/id_ed25519_ops
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACB5pHUVH0BkO7rN80qAD8T2QPjn1GZKcTcf69Ohgj+G3QAAAJjnScHR50nB
0QAAAAtzc2gtZWQyNTUxOQAAACB5pHUVH0BkO7rN80qAD8T2QPjn1GZKcTcf69Ohgj+G3Q
AAAEAA4EDnZkhlaNVlFUK9Ml9TnEnjs5eGHZNlNQBBVuycDnmkdRUfQGQ7us3zSoAPxPZA
+OfUZkpxNx/r06GCP4bdAAAAE29wc0BwaGFudG9tLW9wcy1raXQBAg==
-----END OPENSSH PRIVATE KEY-----
```

### Defensive Architecture Analysis

- **Loopback Binding:** The HTTP daemon on `10.13.37.30` listens only on `127.0.0.1`, blocking direct external TCP network traffic from `10.13.37.2`.
- **ForceCommand / No-TTY Restrictions:** The remote SSH server restricts shell commands and interactive PTY allocation, returning `restricted endpoint` upon normal interactive login.
- **SSH TCP Forwarding Flaw:** The remote SSH configuration permits multiplexed TCP tunneling (`AllowTcpForwarding yes`), allowing client-initiated port forwarding independent of shell access.

---

## 3. Exploitation: SSH Local Port Forwarding (`-L -Nf`)

We establish an encrypted tunnel forwarding our local port `9999` to `127.0.0.1:8080` on the remote target host:

```bash
phantom16@phantom:~$ ssh -i ~/.ssh/id_ed25519_ops -L 9999:127.0.0.1:8080 ops@10.13.37.30 -Nf
```

### Breakdown of Flags:
- **`-L 9999:127.0.0.1:8080`**: Binds local port `9999` and forwards all incoming TCP traffic through the encrypted SSH channel to `127.0.0.1:8080` relative to the remote server.
- **`-N` (No Remote Commands)**: Instructs the client not to execute remote commands or request an interactive shell, bypassing `ForceCommand` and shell enforcement traps.
- **`-f` (Fork to Background)**: Pushes the SSH connection directly into the background before authentication, keeping the active terminal free.

---

## 4. Querying the Internal Service & Flag Extraction

Once the tunnel is active, sending a standard HTTP request to the forwarded local port extracts the flag:

```bash
phantom16@phantom:~$ curl -s http://127.0.0.1:9999
bl_phtm16_9fd69ae362fefb73
```

- **Extracted Flag:** `bl_phtm16_9fd69ae362fefb73`

### Operational Cleanliness (Socket Tear-Down)

Terminating the background tunneling process prevents hanging sockets:

```bash
phantom16@phantom:~$ pkill -f 9999 2>/dev/null
```

---

## 5. Summary of SSH Tunneling Mechanisms

| Tunneling Type | Flag Syntax | Traffic Direction | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **Local Port Forwarding** | `-L <local_port>:<remote_host>:<remote_port>` | Local → Remote | Access loopback/internal services on a remote network |
| **Remote Port Forwarding** | `-R <remote_port>:<local_host>:<local_port>` | Remote → Local | Expose local services (e.g. reverse shell listeners) to remote hosts |
| **Dynamic SOCKS Proxy** | `-D <local_port>` | Local → Multi-destination | Proxy all tool traffic (via `proxychains`) into the target subnet |

---

## 6. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Track** | Phantom Track (Level 16) |
| **Current User** | `phantom16` (`10.13.37.2`) |
| **Remote Service** | `ops@10.13.37.30:8080` (`127.0.0.1`) |
| **Authentication Material** | `~/.ssh/id_ed25519_ops` |
| **Technique** | Non-Interactive SSH Local Port Forwarding (`-L -Nf`) |
| **Discovered Flag** | `bl_phtm16_9fd69ae362fefb73` |

---

## 7. Key Commands & Concepts Reference

- `ssh -i <key> -L <local_port>:<dest_ip>:<dest_port> <user>@<host> -Nf`: Establish a background local port forwarding tunnel.
- `curl -s http://127.0.0.1:<local_port>`: Interrogate loopback services tunneled through the bastion.
- `pkill -f <port>`: Terminate background SSH tunneling processes cleanly.

---

## 8. Lessons Learned & Defensive Takeaways

1. **Shell Restrictions Do Not Block TCP Forwarding:** Restricting interactive shells (`/bin/false`, `ForceCommand`) does not prevent network pivoting unless `AllowTcpForwarding no` is explicitly configured in `/etc/ssh/sshd_config`.
2. **Loopback Binding is Insufficient on Dual-Homed / Shared Bastions:** Binding internal services to `127.0.0.1` protects against external perimeter scans, but any user with SSH authentication to that host can forward traffic directly to loopback.
3. **Anti-Forensic Socket Termination:** Leaving persistent background SSH tunnels open leaves distinct listening sockets in `ss -tuln` and process listings (`ps aux`), creating easily detectable network Indicators of Compromise.
